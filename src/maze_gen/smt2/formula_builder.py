""" Build self.random smt formulas from scratch or using given subexpressions
"""
from typing import FrozenSet
from logging import getLogger

from pysmt.fnode import FNode
import pysmt.operators as ops
import pysmt.typing as types
import pysmt.shortcuts as sc
from pysmt.shortcuts import get_env
from storm.utils.randomness import Randomness # pylint: disable=import-error

from  . import formula_operations

BV_UNARY_OPS = frozenset([ops.BV_NOT, ops.BV_NEG, ops.BV_ROL,ops.BV_ROR])
BV_BINARY_OPS = frozenset([ ops.BV_AND, ops.BV_OR, ops.BV_XOR, ops.BV_ADD, \
                            ops.BV_SUB, ops.BV_MUL, ops.BV_UDIV,\
                            ops.BV_UREM,  ops.BV_SDIV, ops.BV_SREM])
OTHER_BV_OPS = frozenset([ops.BV_ZEXT, ops.BV_SEXT, ops.BV_EXTRACT, ops.BV_CONCAT, ops.BV_COMP, ops.BV_LSHL, ops.BV_ASHR, ops.BV_LSHR])
MY_IRA_OPS = frozenset(filter(lambda t: t not in (ops.BV_TONATURAL, ops.TOREAL, ops.POW),ops.IRA_OPERATORS))


assert BV_UNARY_OPS | BV_BINARY_OPS | OTHER_BV_OPS == ops.BV_OPERATORS
LOGGER = getLogger(__name__)

def get_constants_for_type(node_type: types.PySMTType,is_index_or_shift: bool=False) -> set[FNode] | FrozenSet[FNode]:
    """Returns interesting constants of type node_type"""
    if node_type == types.BOOL:
        return frozenset([sc.FALSE(), sc.TRUE()])
    if node_type == types.INT:
        return frozenset([sc.Int(0), sc.Int(1)])
    if node_type.is_bv_type():
        width = node_type.width # type: ignore
        if is_index_or_shift:
            return set([sc.BVZero(width), sc.BVOne(width)])
        return set([sc.BVZero(width), sc.BVOne(width), sc.BV(2**width - 1, width), sc.BV(2**(width-1), width)])
    return set()

class FormulaBuilder():
    """Builds random formulas using subexpressions from a given seed formula
    :param formula: Seed formula
    :param logic: The logic to use for the built formula
    :param rand: A source of randomness
    """
    def __init__(self, formula: FNode, logic: str, rand: Randomness):
        self.variables_by_type = {}
        for variable in formula_operations.get_nodes(formula, lambda _: True):
            node_type = variable.get_type()
            if variable.get_type() not in self.variables_by_type:
                self.variables_by_type[node_type] = set()
            self.variables_by_type[node_type].add(variable)
        self.logic = logic
        self.bv_types = set(filter(lambda t: t.is_bv_type() and t.width <= 64, self.variables_by_type.keys()))
        if 'BV' in logic and len(self.bv_types) == 0:
            LOGGER.warning("No valid bv types in seed!")
        self.variables_depths = formula_operations.label_formula_depth(formula)
        self.random = rand
        self.arrays = set(filter(lambda t: t.is_array_type(), self.variables_by_type.keys()))
        
    def get_random_assertion(self, max_depth: int):
        """ Build a random boolean formulas of maximum depth 
        """
        res = self.build_formula_of_type(types.BOOL, max_depth)
        return res

    def build_formula_of_type(self, node_type: types.PySMTType, max_depth: int, is_index_or_shift: bool = False) -> FNode:
        """ Build a random formula of the given type and depth """
        if max_depth == 0:
            return self.random.random_choice(self.get_leaves_for_type(node_type, max_depth, is_index_or_shift))
        res = self.random.random_choice(self.get_ops_for_outtype(node_type)\
            + self.get_leaves_for_type(node_type, max_depth, is_index_or_shift))
        
        if isinstance(res, FNode):
            return res
        next_operation, subtypes_needed = res
        node_args = tuple(self.build_formula_of_type(t, max_depth-1, \
                                                    i == 1 and (next_operation in (ops.ARRAY_OPERATORS) or next_operation in \
                                                                                  (ops.BV_LSHL, ops.BV_ASHR, ops.BV_LSHR))) \
                                                                                  for i, t in enumerate(subtypes_needed))
        payload = self.get_payload_for_op(next_operation, node_type, subtypes_needed)
        return get_env().formula_manager.create_node(next_operation, node_args, payload)
    
    def get_ops_for_outtype(self, out_type: types.PySMTType) -> list[tuple[int,list[types.PySMTType]]]:
        """ Returns all possible supported operations for a given SMT-Node Type
            BV Types are restrained to those present in the seed formula
            Only arrays declared in the seed are used, i.e. no new Arrays are created.
        """
        res = []
        if out_type == types.BOOL:
            res.append((ops.NOT,[types.BOOL]))
            res.extend([(o,[types.BOOL, types.BOOL]) for o in filter(lambda o: o != ops.NOT, ops.BOOL_CONNECTIVES)])
            if ('BV' in self.logic):
                res.extend([(o,[t,t]) for o in ops.BV_RELATIONS for t in self.bv_types])
                res.extend([(ops.EQUALS,[t,t]) for t in self.bv_types])
            if ('IA' in self.logic):
                res.extend([(o,[types.INT,types.INT]) for o in ops.IRA_RELATIONS])
                res.append((ops.EQUALS,[types.INT,types.INT]))
        if out_type.is_bv_type():
            res.extend([(o,[out_type]) for o in BV_UNARY_OPS])
            res.extend([(o,[out_type, out_type]) for o in BV_BINARY_OPS])
            # Size changing types:
            res.extend([(o,[smaller_type]) for o in (ops.BV_SEXT,ops.BV_ZEXT) \
                        for smaller_type in filter(lambda st: st.width < out_type.width, self.bv_types)]) #type: ignore
            res.extend([(ops.BV_EXTRACT,[larger_type]) \
                        for larger_type in filter(lambda st: st.width > out_type.width, self.bv_types)]) #type: ignore
            for type1 in self.bv_types:
                for type2 in self.bv_types:
                    if type1.width + type2.width == out_type.width: #type: ignore
                        res.append((ops.BV_CONCAT,[type1,type2]))

        if out_type.is_int_type():
            res.extend([(o,[types.INT, types.INT]) for o in MY_IRA_OPS])

        if 'ABV' in self.logic or 'AL' in self.logic or 'AN' in self.logic:
            arrays_for_out_type = set(filter(lambda at: at.elem_type == out_type, self.arrays))
            if len(arrays_for_out_type) > 0:
                res.extend([(ops.ARRAY_SELECT,[at, at.index_type]) for at in arrays_for_out_type])
                if out_type.is_bool_type():
                    res.extend([(ops.EQUALS,[at,at]) for at in self.arrays])
                if out_type.is_array_type():
                    res.append((ops.ARRAY_STORE,[out_type,out_type.index_type,out_type.elem_type])) #type: ignore
        return res
    
    def get_leaves_for_type(self,node_type: types.PySMTType, maximum_depth: int, is_index_or_shift: bool = False) -> list[FNode]:
        """ Get constants or subexpressions so we don't need to generate subformulas 
        """
        res = list(get_constants_for_type(node_type, is_index_or_shift))
        if node_type in self.variables_by_type:
            res.extend(filter(lambda v: self.variables_depths[v] <= maximum_depth, self.variables_by_type[node_type]))
        if len(res) > 0:
            return res
        return list(self.variables_by_type[node_type])

    def get_payload_for_op(self,op: int, node_type: types.PySMTType, argtypes: list[types.PySMTType]):
        """ Returns the necessary additional information pySMT needs to create a node """
        if op in (ops.BV_ZEXT, ops.BV_SEXT):
            return (node_type.width, node_type.width-argtypes[0].width) #type: ignore
        if op == ops.BV_CONCAT:
            return (argtypes[0].width + argtypes[1].width,) # type: ignore
        if op == ops.BV_EXTRACT:
            diff = argtypes[0].width - node_type.width#type: ignore
            offset = self.random.get_random_integer(0,diff) # type: ignore #
            return (node_type.width, offset, node_type.width+offset-1) #type: ignore
        if op in (ops.BV_ROL, ops.BV_ROR):
            return (argtypes[0].width, self.random.get_random_integer(0,node_type.width-1)) #type: ignore
        if op in ops.BV_OPERATORS:
            return (argtypes[0].width,) # type: ignore
        return None

import random 
import logging

from smt2 import parser, converter # pylint: disable=import-error
import transforms # pylint: disable=import-error

LOGGER = logging.getLogger(__name__)

class Generator:
    def __init__(self, size, edges, sln, smt_file, transformations):
        self.size = size
        self.edges = edges
        self.sln = sln
        self.transformations = transformations
        self.logic = parser.read_file(smt_file).logic

        self.is_sat, self.is_wd = parser.get_forced_parameters(smt_file, transformations)
        try:
            self.constraints, self.vars_all, self.array_size = parser.parse(smt_file, transformations, check_neg = False)
        except Exception as e:
            LOGGER.warning('Error while parsing smt file %s', smt_file)
            LOGGER.exception(e)
            self.constraints = {} if self.is_sat else {'(1==0)': False}
            self.vars_all = {}
            self.array_size = 0

        transforms.remove_constraints(self.constraints, transformations['dc'])
        transforms.make_const(self.vars_all, transformations['mc'])

        self.groups, self.vars = parser.independent_formulas(self.constraints, self.vars_all, self.array_size)

        if transformations['sh']:
            self.groups, self.vars = transforms.coshuffle(self.groups, self.vars)

        self.insert = []
        for _ in range(self.size):
            self.insert.append(0)
        while sum(self.insert) < len(self.groups):
            for func in self.sln:
                self.insert[func] += 1
                if sum(self.insert) >= len(self.groups):
                    break

        if transformations['sh']:
            random.shuffle(self.insert)
            
    def get_logic_def(self):
        logic_def = ""
        
        if 'BV' in self.logic:
            logic_def += converter.get_bv_helpers(self.is_wd)
        if self.array_size > 0:
            logic_def += converter.get_array_helpers(self.array_size)
        return logic_def

    def get_logic_c(self):
        logic_c = []
        group_idx = 0
        for idx in range(self.size):
            if self.insert[idx] == 0 and len(self.edges[idx]) > 1:
                logic_c.append("\t\tsigned char c = __VERIFIER_nondet_char();")
            else:
                tab_cnt = 0
                constraints, variables = [],set()
                for cnt in range(self.insert[idx]):
                    constraints.extend(self.groups[group_idx + cnt])
                    variables = variables.union(self.vars[group_idx + cnt])
                buggy_constraints = ""  
                for var in variables:
                    buggy_constraints += self.get_initialisation(var)
                    

                if len(self.edges[idx]) > 1:
                    buggy_constraints += "\tchar c = __VERIFIER_nondet_char();\n"
                buggy_constraints += "\tint flag = 0;\n"
                for constraint in constraints:
                    buggy_constraints += "\t"*tab_cnt + "\tif{}{{\n".format(constraint)
                    tab_cnt += 1
                buggy_constraints += "\t"*tab_cnt + "\tflag = 1;\n"
                for k in range(len(constraints)-1, -1, -1):
                    buggy_constraints += "\t"*k + "\t}\n"
                logic_c.append(buggy_constraints)
                group_idx += self.insert[idx]
        return logic_c

    def get_initialisation(self, var):
        if '[' in var: #Arrays
            dim = var.count('[')
            width, vartype = self.vars_all[var].split("_")
            if self.transformations['init_arrays']:
                return "\t{} {};\n\tinit({}{},{},{});\n".format(vartype,var,'*'*(dim-1),var.split('[')[0],width,converter.get_array_size_from_dim(dim))
            return "\t{} {};\n".format(vartype,var)
        if self.vars_all[var] == 'bool':
            return "\t_Bool {} = __VERIFIER_nondet_bool();\n".format(var)
        if self.vars_all[var] == 'const bool':
            return "\t const _Bool {} = __VERIFIER_nondet_bool();\n".format(var)
        orig_type = self.vars_all[var]
        short_type = orig_type.split(" ")[-1]
        if 'unsigned' in orig_type:
            short_type = 'u' + short_type
        return "\t{} {} = __VERIFIER_nondet_{}();\n".format(self.vars_all[var], var, short_type)

    def get_guard(self):
        guard = []
        group_idx = 0
        for idx in range(self.size):
            conds_default = [["0"], ["1"],
            ["c < 0", "c >= 0"],
            ["c < -43", "c < 42", "c >= 42"],
            ["c < -64", "c < 0", "c < 64", "c >= 64"]]
            numb_edges = len(self.edges[idx])
            if self.insert[idx] == 0:
                guard.append(conds_default[numb_edges])
            else:
                next_edge, bug_edge, m = 0, 0, 0
                conds = []
                for i in range(len(self.sln)):
                    if self.sln[i] == idx:
                        if i == len(self.sln) - 1:
                            next_edge = 'bug'
                        else:
                            next_edge = self.sln[i+1]
                for n in range(numb_edges):
                    if self.edges[idx][n] == next_edge:
                        bug_edge = n
                for n in range(numb_edges):
                    if n == bug_edge:
                        conds.append("flag == 1")
                    else:
                        conds.append(conds_default[numb_edges-1][m] + " && flag == 0")
                        m += 1
                group_idx += 1
                guard.append(conds)
        return guard
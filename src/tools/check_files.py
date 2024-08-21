""" Checks SMT2-files for good potential candidates  
"""
import os
import sys
import logging
from src.maze_gen.smt2 import formula_operations as ff
from src.maze_gen.smt2 import parser, converter as conv
from src.maze_gen.storm.smt.smt_object import smtObject
from pysmt.shortcuts import reset_env, is_sat, And

LOGGER = logging.getLogger(__name__)

def check_files(file_path: str, resfile: str, sat: str) -> None:
    """Performs various checks on SMT2 files to see if they are valid.
    :param file_path:   Input files. If a directory, recursively check all smt2 files
                        in the directory and subdirectory.
    :param resfile:     Valid files will be written to this path
    """
    sys.setrecursionlimit(10000)
    
    converter = conv.get_converter()
    converter.set_well_defined(sat == 'unsat')
    if os.path.isdir(file_path):
        LOGGER.info("Going into dir %s\n", file_path)
        for file in sorted(os.listdir(file_path)):
            check_files(os.path.join(file_path,file), resfile, sat)
        return
    if not file_path.endswith('.smt2'):
        return
    LOGGER.info("Checking file %s", file_path)
    try:
        env = reset_env()
        env.enable_infix_notation = True
        #Check number of atoms
        LOGGER.info("Check atoms:")
        filedata = parser.read_file(file_path)
        logic = filedata.logic
        clauses = filedata.clauses
        if len(filedata.formula.get_atoms()) < 5:
            raise ValueError("Not enough atoms")
        LOGGER.info("Done")
        formula = filedata.formula

        # Check that satisfiability is easily found
        # (else everything will take a long time to run)
        LOGGER.info("Check sat:")
        so = smtObject(file_path,'temp')
        so.check_satisfiability(20, sat)
        if so.get_final_satisfiability() == "timeout":
            raise ValueError('Takes too long to process')
        if so.get_final_satisfiability() != sat:
            raise ValueError(f"Can't generate {sat} file from this")
        LOGGER.info("Done.")


        # Check that it is satisfiable on bounded integers
        if 'IA' in str(logic) and sat == 'sat':
            LOGGER.info("Check Integers:")
            if not is_sat(And(formula, *ff.get_integer_constraints(formula)),solver_name='z3'):
                raise ValueError('Unsat in range')
            LOGGER.info("Done.")

        if sat == 'unsat':
            min_index, array_ops = ff.get_array_index_calls(formula)
            all_constant = all(map(lambda node: node.args()[1].is_constant(), array_ops))
            if not all_constant and min_index > ff.MAXIMUM_ARRAY_SIZE:
                raise ValueError("Arrays would be too large")
        else:
        # Check that it is satisfiable on bounded arrays
            min_index = 0
            all_constant = False
            try:
                if str(logic).rsplit('_', maxsplit=1)[-1].startswith('A'):
                    LOGGER.info("Check array size:")
                    _,_,min_index,all_constant = parser.get_minimum_array_size_from_file(file_path)
                    LOGGER.info("Done.")
            except ValueError as e:
                # If arrays need to be large and we want sat the file is bad
                if sat=='sat':
                    raise ValueError(f"Can't generate {sat} file from this: {e}") from e

        converter.set_array_indices(ff.get_indices_for_each_array(array_ops) if all_constant else {})

        # Check that everything is understood by the parser
        # and file doesn't get too large
        LOGGER.info("Check parser:")
        clauses = parser.conjunction_to_clauses(formula)
        clause_count = len(clauses)
        for i, clause in enumerate(clauses):
            converter.convert(clause)
            LOGGER.debug("Checking clause %d out of %d", i+1,clause_count)
        LOGGER.info("Done.")

    except (ValueError, RecursionError) as e:
        LOGGER.warning("Error in %s: %s", file_path, str(e))
        os.system(f'rm {file_path}')
        return
    with open(resfile, 'a') as f:
        f.write(file_path + '\n')

def load(argv):
    """Call via __main.py__"""
    check_files(argv[0],argv[1],argv[2])

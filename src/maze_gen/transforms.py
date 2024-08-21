import random
import logging
import typing as t
import math as m
import os
import sys
import subprocess
from pysmt.shortcuts import And, TRUE, Not, is_sat, FALSE

from storm.utils.randomness import Randomness # pylint: disable=import-error
from storm.smt.smt_object import smtObject # pylint: disable=import-error
from storm.fuzzer.fuzzer import generate_mutants # pylint: disable=import-error
from storm.parameters import get_parameters_dict # pylint: disable=import-error
from smt2 import parser, formula_builder as fb, formula_operations


LOGGER = logging.getLogger(__name__)

def remove_constraints(constraints: dict, dc: int):
    curr = len(constraints)
    rm = m.ceil(curr*(dc/100))
    while rm > 0:
        r = random.choice(list(constraints.keys()))
        constraints.pop(r)
        rm -= 1

def make_const(variables: dict, mc: int):
    symbols = list(filter(lambda t: '[' not in t, variables.keys()))
    goal = m.ceil(len(symbols)*(mc/100))
    for _ in range(goal):
        const = symbols.pop(random.randrange(0,len(symbols)))
        variables[const] = 'const ' + variables[const]

ListAElemT = t.TypeVar('ListAElemT')
ListBElemT = t.TypeVar('ListBElemT')

def coshuffle(list_a: list[ListAElemT],list_b: list[ListBElemT]) -> tuple[list[ListAElemT], list[ListBElemT]]:
    temp = list(zip(list_a,list_b))
    random.shuffle(temp)
    r1, r2 = zip(*temp)
    return list(r1), list(r2)

def parse_transformations(t_type: str) -> dict:
    transformations = t_type.split('_')
    shuffle = False
    storm = False
    sat = True
    init_arrays = True
    well_defined = False
    mc = 0
    keep_id = t_type == 'id'
    dc = 0
    dag = 0
    last = False
    neg = False
    ca = False
    fuzz = False
    max_assert = max_depth = 0
    for transformation in transformations:
        if transformation == 'sh':
            shuffle = True
        elif transformation.startswith('storm'):
            storm = True
            max_assert = 20
            max_depth = 10
            if len(transformation) > 5:
                max_assert, max_depth = transformation.removeprefix("storm").split('x')
        elif transformation.startswith('fuzz'):
            fuzz = True
            max_assert = 10
            max_depth = 10
            if len(transformation) > 4:
                max_assert, max_depth = transformation.removeprefix("fuzz").split('x')

        elif transformation == 'wd':
            well_defined = True
        elif transformation.startswith('dc'):
            dc = int(transformation[2:])
        elif transformation == 'keepId':
            keep_id = True
        elif transformation.startswith('mc'):
            mc = int(transformation[2:])
        elif transformation == 'unsat':
            sat = False
        elif transformation.startswith('dag'):
            dag = int(transformation[3:])
        elif transformation == 'last':
            last = True
        elif transformation == 'neg':
            neg = True
        elif transformation == 'ca':
            ca = True
        elif transformation == 'no-init-arrays':
            init_arrays = False
    return {'sh': shuffle, 'dc': dc, 'storm' : storm, 'keepId' : keep_id, 'wd' : well_defined, 'mc' : mc, 'fuzz': fuzz, \
            'sat' : sat, 'dag': dag, 'last': last, 'neg': neg, 'ca': ca, 'max_assert': int(max_assert), 'max_depth': int(max_depth), \
            'init_arrays': init_arrays}

def run_formula_builder(smt_file: str, mutant_path: str, seed: int, n: int, transformations) -> list[str]:
    if n <= 0:
        return []
    LOGGER.info("Building %s new assertions.", n)
    sys.setrecursionlimit(10000)
    filedata = parser.read_file(smt_file)
    if not transformations['sat']:
        core = parser.get_unsat_core(filedata.clauses, filedata.logic)
    builder = fb.FormulaBuilder(filedata.formula, filedata.logic, Randomness(seed))
    mutants = []
    for i in range(n):
        clauses = [builder.get_random_assertion(transformations['max_depth']) for _ in range(transformations['max_assert'])]
        formula = And(*clauses) if transformations['sat'] else And(*clauses,*core)
        sat_status = 'unsat'
        if transformations['sat'] and is_sat(formula,solver_name='z3',logic=filedata.logic):
            sat_status = 'sat'
        respath = os.path.join(mutant_path, f'mutant_{i}_{sat_status}.smt2')
        mutants.append(respath)
        parser.write_to_file(formula,filedata.logic, respath)
    return mutants

def run_storm(smt_file: str, mutant_path: str, seed: int, n: int, transformations: dict) -> list[str]:
    if n <= 0:
        return []
    LOGGER.info("Running Storm.")
    file_data = parser.read_file(smt_file)

    smt_obj = smtObject(smt_file, mutant_path, transformations['sat'])
    smt_obj.check_satisfiability(10*60, 'sat' if transformations['sat'] else 'unsat')
    if smt_obj.get_final_satisfiability() == "timeout":
        LOGGER.warning("Could not fuzz file: timeout.")
        if transformations['sat']:
            return [smt_file] * n
        core = FALSE()
    elif smt_obj.get_final_satisfiability() == "sat" and not transformations['sat']:
        if not 'A' in file_data.logic:
            LOGGER.warning("Could not fuzz file: cannot generate unsat files from sat %s files.", file_data.logic)
            return [smt_file] * n
        # Try to see if we can get an unsat core from array constraints
        min_index, calls  = formula_operations.get_array_index_calls(file_data.formula)
        core = And(formula_operations.get_array_constraints(calls, min_index))
        LOGGER.info("Formula is sat, trying to build core from array constraints.")
        if is_sat(And(core,file_data.formula),solver_name='z3',logic=file_data.logic):
            LOGGER.warning("Could not get core from array constraints, using trivial core.")
            core = FALSE()
    elif transformations['sat']:
        core = TRUE()
    else:
        clauses = [Not(file_data.formula)] if smt_obj.orig_satisfiability != smt_obj.final_satisfiabiliy else file_data.clauses
        core = And(*parser.get_unsat_core(clauses, file_data.logic))

    fpars = get_parameters_dict(False, 0)
    fpars['number_of_mutants'] = n
    fpars['max_depth'] = transformations['max_depth']
    fpars['max_assert'] = transformations['max_assert']

    generate_mutants(smt_obj, mutant_path, fpars['max_depth'],fpars['max_assert'],seed, file_data.logic,fpars)

    mutants = [mutant_path + f'/mutant_{i}.smt2' for i in range(n)]
    if not transformations['sat']:
        for mutant in mutants:
            assertions = parser.read_file(mutant).clauses
            parser.write_to_file(And(*assertions, core),file_data.logic, mutant)
    return mutants 
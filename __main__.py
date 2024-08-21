""" Main entry point, switch functionality and set log_level
"""
import sys
import logging
from src.tools import test, experiment, generate

LOGGER = logging.getLogger(__name__)

PYSMT_INSTALLED = False
try:
    from pysmt.exceptions import SolverAPINotFound
    PYSMT_INSTALLED = True
except ImportError:
    LOGGER.warning("WARNING: pySMT not installed, some features are disabled.")

if PYSMT_INSTALLED:
    try:
        from pysmt.solvers import z3 
    except SolverAPINotFound:
        LOGGER.warning("WARNING: Pysmt installed, but cannot find Z3. Try running python3 -m pysmt install --z3")
        PYSMT_INSTALLED = False
if PYSMT_INSTALLED:
    try:
        from distutils.errors import CompileError
        from pysmt.smtlib.parser import SmtLibParser
        PYSMT_INSTALLED = True
    except CompileError as e:
        LOGGER.warning("WARNING: Pysmt could not compile, is python3.xx-dev installed?")
        LOGGER.warning(e)
        PYSMT_INSTALLED = False
if PYSMT_INSTALLED:
    from src.tools import minimize, check_files

if __name__ == '__main__':
    mode = sys.argv[1]
    if not mode.startswith("--"):
        mode = input("Run tests [t], experiment [e], generate maze [g] or minimize [m]")
        argv = sys.argv[1:]
    else:
        mode = mode[2:]
        argv = sys.argv[2:]
    log = argv[0]
    if not log.startswith("--"):
        LOG = logging.INFO
    else:
        LOG = log[2:]
        if LOG == 'E':
            LOG = logging.ERROR
        elif LOG == 'W':
            LOG = logging.WARNING
        elif LOG == 'I':
            LOG = logging.INFO
        elif LOG == 'D':
            LOG = logging.DEBUG
        argv = argv[1:]
    logging.basicConfig(level=LOG, format='%(levelname)s: %(message)s', style='%')

    if mode == "t":
        test.load(argv)
    elif mode == "m" and PYSMT_INSTALLED:
        minimize.Minimizer(argv).minimize()
    elif mode == "g":
        generate.load(argv)
    elif mode == "e":
        experiment.load(argv)
    elif mode == "c" and PYSMT_INSTALLED:
        check_files.load(argv)
    else:
        LOGGER.error("Invalid mode %s", "" if PYSMT_INSTALLED else "Have you tried installing pysmt?")

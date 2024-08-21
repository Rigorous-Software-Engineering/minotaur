""""Run an experiment"""
import json
import os
import time
import logging

from . import test
from ..runner import commands

LOGGER = logging.getLogger(__name__)

def load_config(path: str) -> dict:
    """ Load experiment configuration from json and set default values
    :param path: Json file path
    """
    with open(path) as f:
        txt = f.read()
    
    conf = json.loads(txt)

    if 'verbosity' not in conf.keys():
        conf['verbosity'] = 'bug_only'
    if 'maze_gen' not in conf.keys():
        conf['maze_gen'] = 'local'
    if 'expected_result' not in conf.keys():
        conf['expected_result'] = 'error'
    if 'abort_on_error' not in conf.keys():
        conf['abort_on_error'] = 1
    if 'avg' not in conf.keys():
        conf['avg'] = 1
    if 'gen_time' not in conf.keys():
        conf['gen_time'] = 30000
    if 'coverage' not in conf.keys():
        conf['coverage'] = 0
    if 'batch_duration' not in conf.keys():
        conf['batch_duration'] = conf['duration']
    if 'check_error' not in conf.keys():
        conf['check_error'] = None
    if 'use_core' not in conf.keys():
        conf['use_core'] = -1


    assert conf['repeats'] > 0
    assert conf['workers'] > 0
    assert conf['memory'] > 0
    assert conf['maze_gen'] in ['local', 'container']
    assert conf['verbosity'] in ['all','summary','bug','bug_only']
    return conf



def load(argv):
    """ Run experiment. Should be called from __main__.py 
    """
    if argv[0].endswith('.conf.json'):
        conf_path = argv[0]
    else:
        conf_path = os.path.join(test.get_minotaur_root(),'experiments',argv[0] + '.conf.json')

    conf = load_config(conf_path)
    outdir = argv[1]

    commands.run_cmd(f'mkdir -p {outdir}')
    with open(os.path.join(outdir, 'times'), 'w') as resfile:
        resfile.write("run_nr, time\n")

        runs = conf['repeats']
        conf['repeats'] = conf['batches']

        variable_keys = list(map(lambda kv: kv[0],(filter(lambda kv: isinstance(kv[1], list), conf.items()))))
        LOGGER.info("Found the following variable keys %s", str(variable_keys))

        for i in range(runs):
            curr_conf = dict(conf)
            for key in variable_keys:
                set_param_value(curr_conf, conf, key, i)
            times = []
            LOGGER.info("Starting experiment %d", i)
            for j in range(conf['avg']):
                start = time.time()
                LOGGER.debug("Staring run %d/%d of experiment %d", j, conf['avg'],i)
                LOGGER.debug("Using conf %s", curr_conf)
                test.main(curr_conf, os.path.join(outdir, f'run{i}_{j}'))
                end = time.time()
                times.append(end-start)
            resfile.write(f"{i},{sum(times)/len(times)}\n")
            resfile.flush()


def set_param_value(new_conf: dict, old_conf: dict, key: str, i: int):
    """ Set new_conf[key] to i-th value of old_conf[key]
    """
    new_conf[key] = old_conf[key][i % len(old_conf[key])]
    LOGGER.debug("Running with value %s for key %s", new_conf[key], key)
    if key == 'parameters' and old_conf['transforms'] == 0:
        new_conf['parameters']['keepId'] = [1]
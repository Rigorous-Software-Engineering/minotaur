"""Run automated tests of program analyzers"""
import random
import sys
import os
import json
import time
import itertools as it
from collections import namedtuple, OrderedDict
from math import ceil
import logging
from typing import Iterable

from ..runner import docker, commands, maze_gen

LOGGER = logging.getLogger(__name__)

REMOVE_CMD = 'rm -r %s'
CP_CMD = 'cp %s %s'



def load_config(path):
    with open(path, 'r') as f:
        txt = f.read()
    conf = json.loads(txt)

    set_default(conf,'verbosity','all')
    set_default(conf,'maze_gen','local')
    set_default(conf,'expected_result','infer')
    set_default(conf,'abort_on_error',[])
    set_default(conf,'check_error',None)
    set_default(conf,'batch_size',1)
    set_default(conf,'gen_time',120)
    set_default(conf,'coverage',False)
    set_default(conf,'use_core', -1)
    set_default(conf,'batch_duration', conf['duration']*conf['batch_size'])


    assert conf['repeats'] != 0
    assert conf['duration'] > 0
    assert conf['workers'] > 0
    assert conf['memory'] > 0
    assert conf['transforms'] >= 0
    assert conf['maze_gen'] in ['local', 'container']
    assert conf['verbosity'] in ['all','summary','bug','bug_only']
    assert conf['expected_result'] in ['error','safe','infer']
    if conf['use_core'] >= 0 and conf['workers'] > 1:
        LOGGER.warning("Using pinned cpu, only using 1 worker instead of %d", conf['workers'])
        conf['workers'] = 1

    return conf

def resolve_seed_path(seed: str):
    if seed.startswith('/Minotaur/'):
        return os.path.join(get_minotaur_root(),seed.removeprefix('/Minotaur/'))
    return seed

def pick_values(value: dict[str,int]  | list, head: str = "",tail: str = "") -> str | None:
    """
    Randomly pick values in the from either a list or a min/max range.
    If the picked value is 0 nothing is returned, if the value is 1 only the head and tail 
    :param value: Either a list or a dict containing 'min' and 'max' keys
    :param head: String to prepend to the picked value
    :param tail: String to append to the picked value
    """
    if isinstance(value,dict):
        body = str(random.randint(value['min'], value['max']))
    else:
        choice = random.choice(value)
        if choice == 0:
            if head == '' and tail == '':
                return None
            return ''
        if choice == 1:
            body = ''
        else:
            body = str(choice)
    return head + body + tail

def set_default(parameters: dict, name: str, value):
    """
    Set option name in parameters to 'value' if it is already set.
    """
    if name not in parameters.keys():
        parameters[name] = value
        LOGGER.debug('Using default value %s for parameter %s', value, name)        

def get_random_params(conf: dict):
    """
    Pick random maze parameters from the options given in the config
    """
    conf['repeats'] -= 1
    params = conf['parameters']
    res = {}
    for key, value in params.items():
        if key == 't':
            body = ''
            for tkey, tvalue in value.items():
                transform = pick_values(tvalue, tkey,  '_')
                body += transform if transform is not None else ''
            body = body.strip('_') # remove last _
        elif key == 's':
            body = resolve_seed_path(value)
            while os.path.isdir(body):
                body = os.path.join(body,random.choice(os.listdir(body)))
        else:
            body = pick_values(value)

        if body is not None:
            res[key] = body

    # default values
    set_default(res,'a','Backtracking')
    set_default(res,'w',5)
    set_default(res,'h',5)
    set_default(res,'b','ve')
    set_default(res,'n',1)
    set_default(res,'t','keepId')
    set_default(res,'r',int(time.time()))
    set_default(res,'c',0)
    set_default(res,'g','default_gen')
    set_default(res,'m',int(conf['transforms']))

    if 'u' in res:
        res['w'] = 1
        res['h'] = 1
        res['u'] = ''
    elif int(res['w']) < 5 and int(res['h']) < 5:
        res['h'] = 5 # mazelib gets stuck when generating 4x4 or smaller mazes
    return res

def pick_tool_flags(conf: dict, tool: str):
    """
    Pick random parameters for a tool from the options given in conf
    """
    variant  = random.choice(conf['tool'][tool]['variant'])
    flags = ""
    if 'toggle' in conf['tool'][tool].keys():
        for opt in conf['tool'][tool]['toggle']:
            if random.randint(0,1) == 1:
                flags += opt + ' '
    if 'choose' in conf['tool'][tool].keys():
        for flag, options in conf['tool'][tool]['choose'].items():
            chosen = random.choice(options)
            if chosen != 0:
                flags += flag + chosen + ' '
    return variant,flags


Target = namedtuple(typename='Target',field_names=['maze','tool','index','params','variant','flags'])

class TargetGenerator(Iterable):
    """ Keep track of everything we need to run.
    The iterator returns batches of targets which can then be run in a docker. Handles:
        - randomly picking parameters and tool flags,
        - generating mazes at the right time,
        - splitting up generated mazes into batches and writing batchfiles.
        - keep count of generated batches to finish after the given number of repeats.
    """
    def __init__(self, conf):
        self.conf = conf
        self.repeats = self.conf['repeats'] if self.conf['repeats'] >= 0 else sys.maxsize
        self.targets = []
        self.mazes = OrderedDict()

    def __iter__(self):
        return self

    def __next__(self):
        while len(self.targets) == 0:
            if not(self.has_targets()):
                LOGGER.info("All batches generated")
                raise StopIteration

            LOGGER.info("Out of targets, fetching new batch.")
            self.add_batch()
        return self.targets.pop(0)

    def has_targets(self):
        return self.repeats > 0 or len(self.targets) > 0 or len(self.mazes) > 0

    def add_batch(self):
        """ Fetch a new batch.
        If there are not enough mazes, generate new ones.
        If we have already genearted all batches, this does nothing.
        """
        while len(self.mazes) < self.conf['batch_size'] and self.repeats > 0:
            LOGGER.info("Out of mazes, generating more.")
            self.generate_mazes()

        self.repeats -= 1
        batch_id = random.randint(0,65535)

        maze_keys = list(self.mazes.keys())
        maze_count = min(len(maze_keys),self.conf['batch_size'])
        if self.conf['expected_result'] == 'infer':
            with open(get_result_file(batch_id), 'w') as res_file:
                expected_results = self.get_expected_results(maze_keys)
                maze_count = min(len(expected_results), maze_count)
                for i in range(maze_count):
                    res_file.write(f"{maze_keys[i]} {expected_results[i]}\n")

        with open(get_batch_file(batch_id), 'w') as batch_file:
            for i in range(maze_count):
                batch_file.write(f"{docker.HOST_NAME}/{maze_keys[i]}\n")

        for tool in self.conf['tool'].keys():
            variant, flags = pick_tool_flags(self.conf,tool)
            for i in range(maze_count):
                maze = maze_keys[i]
                params = self.mazes[maze]
                self.targets.append((False,Target(maze, tool,batch_id, params, variant, flags)))



        if len(self.targets) > 0:
            self.targets[-1] = (True, self.targets[-1][1])

        for i in range(maze_count):
            self.mazes.pop(maze_keys[i])

    def get_expected_results(self, maze_keys):
        expected_results = []
        not_found = 0
        for i in range(min(len(maze_keys),self.conf['batch_size'])):
            maze = maze_keys[i-not_found]
            params = self.mazes[maze]
            res = None
            try:
                res = get_expected_result(params,maze_gen.get_params_from_maze(maze)['m'], self.conf)
                LOGGER.info("Expected result: %s", res)
            except FileNotFoundError:
                pass
            if res is None:
                LOGGER.warning("Could not determine expected result")
                maze_keys.pop(i-not_found)
                self.mazes.pop(maze)
                not_found = not_found+1
                continue
            expected_results.append(res)
        return expected_results

    def generate_mazes(self):
        """ Generate more mazes
        If we are generating in containers, eagerly generate many mazes to utilize as many workers as possible.
        """
        if self.conf['maze_gen'] == 'container':
            paramss = self.fetch_maze_params()
            LOGGER.info("Generating %d more mazes.", len(paramss))
            maze_gen.generate_mazes(paramss, get_temp_dir(),self.conf['workers'],self.conf['gen_time'], use_core=self.conf['use_core'])
            for params in paramss:
                self.mazes.update({maze: params for maze in maze_gen.get_maze_names(params)})
        else:
            params = get_random_params(self.conf)
            maze_gen.generate_maze(params, get_temp_dir(), get_minotaur_root())
            self.mazes.update({maze: params for maze in maze_gen.get_maze_names(params)})

    def fetch_maze_params(self) -> list[dict]:
        """ Get as many maze parameters as needed to fully saturate workers
        """
        mazes_per_batch = ceil(self.conf['batch_size']/max(1,self.conf['transforms']))
        batches_in_parallel = ceil(self.conf['workers']/len(self.conf['tool']))
        return [get_random_params(self.conf) for _ in range(min(self.repeats*mazes_per_batch,batches_in_parallel*mazes_per_batch))]


def get_expected_result(params,maze_id,conf):
    if conf['expected_result'] != 'infer':
        return conf['expected_result']
    if 'storm' in params['t']:
        return 'error' if 'unsat' not in params['t'] else 'safe'
    if 'fuzz' in params['t'] and 'unsat' in params['t']:
        return 'safe'
    if maze_id == 0 and 's' in params:
        with open(params['s']) as seedfile:
            content = seedfile.read()
            if '(set-info :status unsat)' in content:
                return 'safe'
            if '(set-info :status sat)' in content:
                return 'error'
            return None
    smt_dir = os.path.join(get_temp_dir(), 'smt', str(params['r']))
    for file in os.listdir(smt_dir):
        file = str(file)
        if file == f'mutant_{maze_id - 1}_sat.smt2' or file == f'mutant_{maze_id - 1}_unsat.smt2':
            res = 'error' if file.removesuffix('.smt2').rsplit('_',1)[1] == 'sat' else 'safe'
            commands.run_cmd(f"rm {os.path.join(smt_dir, file)}")
            return res
    return None


def fetch_works(conf: dict, gen: TargetGenerator) -> tuple[list[Target], list[Target]]:
    """ Get necessary workesr and mazes we need to delete
    """
    new_targets = list(it.islice(gen, 0, conf['workers']*conf['batch_size']))
    return list(map(lambda w: w[1],new_targets)), list(map(lambda w : w[1], filter(lambda w: w[0], new_targets)))


def get_temp_dir() -> str:
    """ Get the temporary directory in use
    Should be an absolute path
    """
    return os.path.join('/tmp','minotaur_mazes')

def get_maze_dir(maze: str = '') -> str:
    """ Get the temporary directory for mazes.
    :param maze: Optionally get the full path for a specific maze.
    """
    return os.path.join(get_temp_dir(),'src', maze)

def get_batch_file(batch: int) -> str:
    """ Get the batch file for a given batch.
    Batchfiles contain a list of mazes and 
    are used to tell solvers of each batch which mazes to solve.
    """
    return get_maze_dir(docker.BATCH_FILE_FORMAT % batch)

def get_result_file(batch: int) -> str:
    """ Get the expected result file for a given batch.
    Result files contain the maze names + their expected results.
    """
    return get_maze_dir(docker.RESULT_FILE_FORMAT % batch)

def get_minotaur_root() -> str:
    """ Get the dir from which __main__ was called, which is likey
        to be the Minotaur root directory.    
    """
    mainfile = sys.modules['__main__'].__file__ # pylint: disable=no-member 
    return os.path.dirname(os.path.realpath('' if mainfile is None else mainfile))


def get_containers_needed(conf: dict, works: list[Target]):
    """Compute the containers needed for the given workload"""
    return min(ceil(len(works)/conf['batch_size']), conf['workers'])

def spawn_containers(conf: dict, works: list[Target]):
    """Spawn containers for the given workload"""
    procs = []
    for i in range(get_containers_needed(conf,works)):
        target = works[i*conf['batch_size']]
        procs.append(docker.spawn_docker(conf['memory'], target.index, target.tool,get_maze_dir(),conf['use_core'],True))
    commands.wait_for_procs(procs)
    time.sleep(5)

def run_tools(conf: dict,works: list[Target]):
    """Run the tools on the given workload.
    Call after spawn_containers()"""
    duration = conf['duration']
    procs = []
    for i in range(get_containers_needed(conf, works)):
        target  = works[i*conf['batch_size']]
        procs.append(docker.run_docker(duration, conf['batch_duration']*conf['batch_size'], target.tool, target.index, variant=target.variant, flags=target.flags, batch_id=target.index))
    commands.wait_for_procs(procs)
    time.sleep(3)

def store_outputs(conf: dict, out_dir: str, works: list[Target]):
    has_bug = False
    procs = []
    for i in range(get_containers_needed(conf,works)):
        target = works[i*conf['batch_size']]
        procs.append(docker.collect_docker_results(target.tool, target.index, conf['expected_result'], conf['verbosity'],batch_id =target.index))
    commands.wait_for_procs(procs)
    time.sleep(5)

    for i in range(get_containers_needed(conf,works)):
        w = works[i*conf['batch_size']]
        out_path = os.path.join(out_dir, w.tool, str(w.index))
        os.system(f'mkdir -p {out_path}')
        docker.copy_docker_results(w.tool, w.index, out_path)
        if not conf['coverage']:
            docker.kill_docker(w.tool, w.index)
    time.sleep(5)


    for w in works:
        # Write file details into summary
        runtime = 'notFound'
        tag = 'notFound'
        out_path = os.path.join(out_dir, w.tool, str(w.index), w.maze)
        if os.path.isdir(out_path):
            for filename in os.listdir(out_path):
                if len(filename.split('_')) == 2:
                    runtime, tag = filename.split('_')
                    if tag in conf['abort_on_error']:
                        if conf['check_error'] is None:
                            has_bug = True
                        elif not has_bug:
                            has_bug = not check_error(conf, w, tag, out_dir)
                    commands.run_cmd(CP_CMD % (get_maze_dir(w.maze), out_path)) # Keep buggy mazes
                    write_summary(conf, out_dir, w, tag, runtime)
        if runtime == 'notFound' or tag == 'notFound':
            write_summary(conf, out_dir, w, tag, runtime)
    return has_bug


def check_error(conf: dict, w: Target, tag: str, out_dir: str):
    out_dir = os.path.join(out_dir, 'check')
    w.params['m'] = maze_gen.get_params_from_maze(w.maze)['m']
    maze = w.maze
    res = 'error' if tag == 'fn' else 'safe'
    if res is None:
        LOGGER.warning("Could not find expected result when trying to check target %s", w)
        return
    docker.run_pa(conf['check_error'][w.tool], w.variant, w.flags, 'check', w.params, out_dir,
                  memory=conf['memory'], timeout=conf['duration']+60, maze=get_maze_dir(maze), expected_result=res) # Add a minute for buffer
    resdir = os.path.join(out_dir,maze, maze)
    if not os.path.isdir(resdir):
        return False # timeout

    for file in os.listdir(resdir):
        if len(file.split('_')) == 2:
            LOGGER.info(file)
            commands.run_cmd('mkdir -p %s' % os.path.join(out_dir,'runs'))
            commands.run_cmd('mv %s %s' % (os.path.join(resdir,file), os.path.join(out_dir,'runs')))
            commands.run_cmd('rm -r %s' % os.path.join(out_dir,maze))
            if tag in file:
                return True
    return False

def write_summary(conf,out_dir, target,tag,runtime):
    maze, tool, batch_id, params, variant, flags = target
    out_path = os.path.join(out_dir,tool, str(batch_id),maze)
    if (conf['verbosity'] == 'bug' or conf['verbosity'] == 'bug_only') and tag not in ('fp', 'fn'):
        commands.run_cmd(REMOVE_CMD % out_path)
        if conf['verbosity'] == 'bug_only':
            return
    with open(out_dir + '/summary.csv', 'a') as f:
        u = '0' if 'u' not in params.keys() else '1'
        f.write(tool + ',' + str(batch_id) + ',' + variant + ',' + flags + ',' + str(maze_gen.get_params_from_maze(maze)['m']) + ',' + u + ',')
        for key, value in params.items():
            if key == 's':
                f.write(str(params['s'].split('/')[-1] + ','))
            elif key == 'u':
                continue # We already wrote u 
            elif key in conf['parameters'].keys():
                f.write(str(value) + ',')
        f.write(f'{runtime},{tag}')
        f.write('\n')
    if conf['verbosity'] == 'summary':
        commands.run_cmd(REMOVE_CMD % out_path)


def write_summary_header(conf, out_dir) -> None:
    with open(out_dir + '/summary.csv', 'w') as f:
        f.write('tool,batch,variant,flags,id,u,')
        for key in conf['parameters'].keys():
            if key != 'u':
                f.write(str(key)+',')
        f.write('runtime,status\n')

def cleanup(completed: 'list[Target]') -> None:
    procs = []
    while(len(completed) > 0):
        target = completed.pop()
        procs.append(commands.spawn_cmd(REMOVE_CMD % get_maze_dir(target.maze)))
        procs.append(commands.spawn_cmd(REMOVE_CMD % get_batch_file(target.index)))
        procs.append(commands.spawn_cmd(REMOVE_CMD % get_result_file(target.index)))
    commands.wait_for_procs(procs)

def store_coverage(conf,works: list[Target], out_dir: str) -> None:
    procs = []
    for i in range(get_containers_needed(conf,works)):
        work = works[i*conf['batch_size']]
        procs.append(docker.collect_coverage_info(work.tool,work.index,f"{work.tool}_{work.index}.cov"))
    commands.wait_for_procs(procs)

    for i in range(get_containers_needed(conf,works)):
        work = works[i * conf['batch_size']]
        docker.copy_docker_results(work.tool, work.index,os.path.join(out_dir,'cov'), docker_dir=docker.COVERAGE_DIR)
        docker.kill_docker(work.tool, work.index)

def main(conf, out_dir):
    os.system(f'mkdir -p {out_dir}')
    if 'seed' in conf.keys():
        random.seed(conf['seed'])
    if conf['coverage']:
        os.system(f"mkdir -p {os.path.join(out_dir, 'cov')}")

    write_summary_header(conf, out_dir)
    done = False

    gen = TargetGenerator(conf)
    while gen.has_targets() and not done:
        works, to_remove = fetch_works(conf, gen)
        spawn_containers(conf, works)
        run_tools(conf, works)
        done = store_outputs(conf, out_dir, works)
        cleanup(to_remove)
        if conf['coverage']:
            store_coverage(conf,works,out_dir)

def load(argv):
    if argv[0].endswith('.conf.json'):
        conf_path = argv[0]
    else:
        conf_path = os.path.join(get_minotaur_root(),'test',argv[0] + '.conf.json')
    out_dir = argv[1]
    conf = load_config(conf_path)
    main(conf, out_dir)

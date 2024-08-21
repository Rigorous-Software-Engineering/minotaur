""" Provides commands and shortcuts for generating mazes
"""
import os
from . import docker, commands

GENERATE_CMD = '%s/scripts/generate.sh -o %s %s'

def get_params_from_maze(maze: str,smt_path = '') -> dict:
    """ Extracts maze parameters from the maze name.
    :param smt_path: Directory of the seed file, if one is used.
    """
    params = {}
    params['a'], size, params['r'], _, *params['t'], params['m'], params['c']= maze.split('percent')[0].split('_')
    *params['g'],_, params['b'] = maze.split('percent')[1][1:].split('_')

    params['w'], params['h'] = map(int, size.split('x'))
    params['m'] = int(params['m'][1:]) # cut 't'
    params['r'] = int(params['r'])
    params['g'] = '_'.join(params['g'])
    params['t'] = '_'.join(params['t'])
    if size == '1x1':
        params['u'] = ''
    if smt_path != '':
        params['s'] = os.path.join(smt_path,params['g'] + '.smt2')
        params['g'] = 'CVE_gen'
    else:
        params['g'] += 'gen'
    return params


def get_maze_names(p):
    """ Returns the maze name assosiated with the given parameters.
        If transformatinons are perforemd, returns one name per transformation.
        :param p: Maze parameters"""
    if p['g'] in ('CVE_gen', 'CVE-neg_gen'):
        generator = f"{p['s'].split('/')[-1][0:-5]}_gen"
    else:
        generator = p['g']
    min_transform = 0 if 'keepId' in p['t'] else 1
    return [f"{p['a']}_{p['w']}x{p['h']}_{p['r']}_0_{p['t']}_t{i}_{p['c']}percent_{generator}_ve.c"\
            for i in range(min_transform,p['m'] + 1)]

def generate_maze_in_docker(params, name: int = 0, timeout=-1):
    """Generate a maze in a running docker container"""
    params['o'] = docker.HOST_NAME
    param_string = get_string_from_params(params)
    cmd = './Minotaur/scripts/generate.sh ' + param_string
    return docker.spawn_cmd_in_docker(docker.get_container('gen', name),  cmd, timeout=timeout)

def setup_generation_docker(params, outdir, index: int):
    """Spawn a container for maze generation and setup seed and output structure.
    :param params: Generation parameters
    :param outdir: Output directory
    :param index: Maze name"""
    if 'r' not in params:
        params['r'] = 1
    commands.run_cmd('mkdir -p ' + outdir + ' ' + ' '.join([os.path.join(outdir, i) for i in ['src','smt','sln','png','txt','bin',f"smt/{params['r']}"]]) )
    docker.spawn_docker(1, index, 'gen', outdir, cpu=index).wait()
    if 's' in params.keys():
        docker.set_docker_seed(params['s'], index, 'gen').wait()

def get_string_from_params(params):
    """Generate a string for generate.sh from a parameter dictionary"""
    param_string = ''
    for param, value in params.items():
        if param == 's':
            value = '/home/maze/' + params['s'].split('/')[-1]
        param_string += f'-{param} {value} '
    return param_string

def get_params_from_string(param_string):
    """Read the parameters from string form into a dictionary"""
    params = {}
    options = param_string.split(' ')
    i = 0
    while i < len(options):
        arg = options[i][1:] #cut the -
        if i == len(options)-1 or options[i+1].startswith('-'):
            if arg == 'u':
                params['w'] = 1
                params['h'] = 1
            value = ""
        else:
            value = options[i+1]
            i+=1
        params[arg] = value
        i+=1
    return params


def generate_mazes(paramss, outdir, workers=1, timeout=-1, use_core=-1):
    if use_core >= 0:
        workers = 1
    works = [[] for _ in range(workers)]
    for i , params in enumerate(paramss):
        works[i % workers].append(params)
    works = list(filter(lambda w: len(w) > 0, works))

    pipes = []
    for i, work in enumerate(works):
        setup_generation_docker(work[0], outdir, i if use_core < 0 else use_core)
        pipes.append(generate_maze_in_docker(work[0],i if use_core < 0 else use_core,timeout))

    longest_work = 0 if len(works) == 0 else max(map(len,works))
    for i in range(1,longest_work):
        for j, work in enumerate(works):
            j = j if use_core < 0 else use_core
            if i < len(work):
                pipes[j].wait()
                commands.run_cmd('mkdir -p ' + os.path.join(outdir, 'smt', str(work[i]['r'])))
                if 's' in work[i]:
                    docker.set_docker_seed(work[i]['s'], j, 'gen').wait()
                pipes[j] = generate_maze_in_docker(work[i], j, timeout)
    commands.wait_for_procs(pipes)
    if use_core > 0:
        docker.kill_docker('gen', use_core)
    else:
        for i in range(len(works)):
            docker.kill_docker('gen',i)

def generate_maze(params, out_dir = '', minotaur = ''):
    if(minotaur == ''):
        import __main__
        minotaur = '/'.join(__main__.__file__.split('/')[:-1])
    param_string = ''
    for param, value in params.items():
        param_string += '-%s %s ' % (param, value)
    out_dir = os.path.join(minotaur, 'temp') if out_dir == '' else out_dir
    return commands.run_cmd(GENERATE_CMD % (minotaur, out_dir, param_string), True)

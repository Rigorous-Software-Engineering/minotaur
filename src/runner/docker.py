"""Provides functions for managing dockers, both for tools and generation"""
import subprocess
import os
import logging
from . import commands, maze_gen

LOGGER = logging.getLogger(__name__)

HOST_NAME = '/mazes'
BATCH_FILE_FORMAT = 'batch_%d.txt'
RESULT_FILE_FORMAT = 'result_%d.txt'
COVERAGE_DIR = 'coverage'
GENERATION_DIR = 'outputs'

DOCKER_PREFIX = 'minotaur-'
DOCKER_COMMAND = 'docker'

SPAWN_CMD_CPU = f'{DOCKER_COMMAND} run --rm -m=%dg -t -d --cpus=1 --cpuset-cpus=%d --name %s --mount type=bind,source=%s,destination={HOST_NAME}%s %s'
SPAWN_CMD_NOCPU = f'{DOCKER_COMMAND} run --rm -m=%dg -t -d --cpus=1 --name %s --mount type=bind,source=%s,destination={HOST_NAME}%s %s'
CP_MAZE_CMD = DOCKER_COMMAND + ' cp %s %s:/home/%s/%s'
CP_SEED_CMD = DOCKER_COMMAND + ' cp %s %s:/home/%s/%s'
CP_CMD = DOCKER_COMMAND + ' cp %s:/home/%s/workspace/%s %s'
KILL_CMD = DOCKER_COMMAND + ' kill %s'
REMOVE_CMD = DOCKER_COMMAND + ' rm %s'

SUPPORT_COVERAGE = ['cbmc', 'esbmc', 'seahorn']

def spawn_cmd_in_docker(container, cmd_str, timeout=-1) -> subprocess.Popen: #type: ignore
    """Spawns a command in a running docker container
    :param container: The container (see get_container)
    :param cmd_str: The command as a string (' ' as sep)
    :param timeout: Run command with timeout; -1 for no limit
    """
    cmd_prefix =  f'{DOCKER_COMMAND} exec {container} /bin/bash -c'
    if timeout > 0:
        cmd_prefix = f'{DOCKER_COMMAND} exec {container} timeout -k 10s {timeout}s /bin/bash -c'
    cmd_args = cmd_prefix.split()
    cmd_args += [cmd_str]
    LOGGER.info('Executing (in container %s): %s', container, ' '.join(cmd_args[3:]))
    try:
        if LOGGER.getEffectiveLevel() == logging.DEBUG:
            return subprocess.Popen(cmd_args, text=True)
        return subprocess.Popen(cmd_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.SubprocessError as e:
        LOGGER.error(e)
def run_cmd_in_docker(container,cmd_str):
    """Spawns a command in a running docker container and wait for it to finish
    :param container: The container (see get_container)
    :param cmd_str: The command as a string (' ' as sep)
    """
    return spawn_cmd_in_docker(container,cmd_str).wait()


def get_user(tool):
    """ Return the username in the given docker; useful when using a prebuilt docker 
    """
    return 'maze'

def get_container(tool: str,name: str | int):
    """Get container name from tool and name"""
    return tool + '-' + str(name)

def clean_name(name) -> str:
    """Make sure 'name' is a valid container name"""
    return str(name).replace(' ', '').replace('=','')

def spawn_docker(memory: int | str, name: int | str, tool: str, maze_dir: str, cpu: int = -1, host_is_readonly: bool=False):
    """Spawns a docker (without running a command yet)
    :param memory:          RAM allocated to docker (in GB)
    :param name:            Container name
    :param tool:            Container tool
    :param maze_dir:        Temporary dir where mazes are either written to or acessed
    :param cpu:             If > 0, bind docker to a specific CPU
    :param host_is_readonly:Whether the docker needs to write into maze_dir  
    """
    if cpu >= 0:
        cmd = SPAWN_CMD_CPU % (memory, cpu, get_container(tool,name), os.path.abspath(maze_dir), ',readonly' if host_is_readonly else '', DOCKER_PREFIX + tool)
    else:
        cmd = SPAWN_CMD_NOCPU % (memory, get_container(tool,name), os.path.abspath(maze_dir), ',readonly' if host_is_readonly else '', DOCKER_PREFIX + tool)
    return commands.spawn_cmd(cmd)

def set_docker_seed(path, name, tool):
    """Set the seed for a container"""
    cmd = CP_SEED_CMD % (path, get_container(tool,name),get_user(tool), os.path.split(path)[1])
    return commands.spawn_cmd(cmd)

def run_docker(duration, batch_duration, tool, name, variant='', flags='', batch_id=0):
    """Run a tool docker
    :param duration: Duration per maze
    :param tool: The tool to run
    :param name: Container name
    :param variant, flags: Optionally variant and flags of tools
    :param batch_id: Id of the batchfile to run (Batchfiles contain mazesto test) 
    """
    user = get_user(tool)
    script = f'/home/{user}/tools/run_{tool}.sh'
    src_path = f'{HOST_NAME}/{BATCH_FILE_FORMAT % batch_id}'
    cmd = ' '.join(map(str,[script, src_path, duration,variant,flags]))
    return spawn_cmd_in_docker(get_container(tool,name), cmd, batch_duration)

def collect_docker_results(tool: str,name: str | int, expected_result: str, verbosity: str ='all', batch_id=0):
    """Collects results of a docker, giving duration and results in simplified format"""
    user = get_user(tool)
    expected_result = f'{HOST_NAME}/{RESULT_FILE_FORMAT % batch_id}' if expected_result == 'infer' else expected_result
    cmd = f"python3 /home/{user}/tools/get_tcs.py /home/{user}/workspace/{GENERATION_DIR} {verbosity} {expected_result}"
    return spawn_cmd_in_docker(get_container(tool,name), cmd)

def copy_docker_results(tool, name , out_path, docker_dir=GENERATION_DIR):
    """Copy results of a docker to out_path"""
    user = get_user(tool)
    return copy_docker_output(tool, name, out_path, user, docker_dir)

def copy_docker_output(tool, name, out_path, user, docker_dir=GENERATION_DIR):
    """Copy output of a docker to out_path"""
    cont = get_container(tool,name)
    if not os.path.isdir(out_path):
        return commands.run_cmd(CP_CMD % (cont, user, docker_dir, out_path))
    if os.path.isdir(os.path.join(out_path,'src')):
        for res_dir in ['src','smt','png','txt','smt','bin']:
            return commands.run_cmd(CP_CMD % (cont, user, os.path.join(docker_dir,res_dir,'.'), os.path.join(out_path, res_dir)))
    return commands.run_cmd(CP_CMD % (cont, user, f'{docker_dir}/.', out_path))

def kill_docker(tool,name):
    """Kills a docker"""
    cmd = KILL_CMD % (get_container(tool,name))
    return commands.spawn_cmd(cmd)

def collect_coverage_info(tool,name, outfile):
    """Collect coverage info for a Docker"""
    if not tool in SUPPORT_COVERAGE:
        raise ValueError("Tool does not support coverage at the moment")
    user = get_user(tool)
    return spawn_cmd_in_docker(get_container(tool,name), f'/home/{user}/tools/get_coverage.sh /home/{user}/workspace/{COVERAGE_DIR} {outfile}')

def run_pa(tool,variant,flags, name, params,outdir, memory = 4,  timeout=60, gen='container', expected_result='error', verbosity='all', maze=''):
    """Generate a maze and run a program analyzer on it.
    :param tool,variant,flags: Program analyzer to test
    :param params: Parameters for maze gen
    :param outdir: Outdir for the results
    :param memory: Memory to use (in GB)
    :param timeout: Timeout for the tool (in seconds)
    :param gen: ['container'|'local'] Generate tool in container or locally
    :param expected_result: ['safe'|'error'] kind of program generated
    """
    commands.run_cmd(f"mkdir -p {os.path.join(outdir,'src')}")
    if maze=='':
        if gen == 'container':
            maze_gen.setup_generation_docker(params,outdir,name)
            maze_gen.generate_maze_in_docker(params,name).wait()
            kill_docker('gen', name)
        else:
            maze_gen.generate_maze(params,outdir)
        t_index = params['m'] - (0 if 'keepId' in params['t'] else 1)
        maze = maze_gen.get_maze_names(params)[t_index]
    else:
        _, maze_name = os.path.split(maze)
        commands.run_cmd(f"cp {maze} {os.path.join(outdir, 'src', maze_name)}")
        maze = maze_name
    commands.run_cmd(f"mkdir -p {os.path.join(outdir,'src')}")
    with (open(os.path.join(outdir, 'src', BATCH_FILE_FORMAT % 0),'w')) as batchfile:
        batchfile.write(f'{HOST_NAME}/{maze}')
    spawn_docker(memory,name,tool,os.path.join(outdir,'src')).wait()
    run_docker(timeout, timeout, tool, name, variant,flags).wait()
    collect_docker_results(tool,name,expected_result,verbosity).wait()
    copy_docker_results(tool,name,os.path.join(outdir, maze))
    kill_docker(tool,name).wait()
""" Implements minimization algorithm 
"""
import os
import logging
from math import ceil

from ..runner import maze_gen, commands, docker
from ..maze_gen.smt2 import parser as sp

LOGGER = logging.getLogger(__name__)

class Minimizer:
    """ As we have a lot of local state, use a class instead of load()
    :param argv:    The argv after the --m (and possibly debug) flag
    """
    def __init__(self,argv: list[str]):
        if ',' in argv[0]:
            run = argv[0][:-1] if argv[0].endswith(',') else argv[0]
            args = run.split(',')
            if len(args) == 16:
                self.tool,self.batch_id,self.variant,self.flags,index,u,a,w,h,c,t,g,s,r,timeout,self.err = args
            else:
                self.tool,self.batch_id,self.variant,self.flags,index,u,a,w,h,t,g,s,r,timeout,self.err = args
                c = 0

            self.timeout = ceil(float(timeout)) + 60 # Add a minute for buffer
            self.seeddir = find_seed_dir(argv[1], s)
            if self.seeddir is None:
                raise ValueError(f"Could not find seed in dir {argv[1]}.")
            LOGGER.debug("Found seed in dir %s", self.seeddir)
            self.outdir = argv[2]
            self.gen = argv[3]
            self.params= {'m':int(index),'a':a,'w':int(w),'h':int(h),'c':int(c),'t':('last_' + t).strip('_'),'g':g,'s':os.path.join(self.seeddir,s+('' if s.endswith('.smt2') else '.smt2')),'r':int(r)}
            if u == '1':
                self.params['u'] = ''
        else:
            maze = argv[0]
            self.seeddir = argv[1]
            self.outdir = argv[2]
            self.timeout = int(argv[3])
            self.gen = argv[4]
            self.err = argv[5]
            self.tool = argv[6]
            self.variant = self.flags = ''
            if len(argv) >= 8:
                self.variant = argv[7]
                self.flags = ' '.join(argv[8:])
            self.params= self.get_params(maze)
        self.expected_result = 'safe' if self.err in ('fp','tn') or 'unsat' in self.params['t'] else 'error'
        self.core = set()


    def minimize(self):
        """Run the minimization"""
        commands.run_cmd('mkdir -p %s' % self.outdir)
        commands.run_cmd("mkdir -p %s" % os.path.join(self.outdir,'seeds'))
        commands.run_cmd("mkdir -p %s" % os.path.join(self.outdir,'runs'))

        if not self.result_is_err(False):
            logging.error('Original maze not a %s', self.err)
            return

        self.minimize_maze()
        seed = self.get_seed()
        self.set_fake_params()

        clauses,self.logic = read_mutant(seed)
        if self.expected_result == 'safe':
            clauses, self.core = self.separate_unsat_core(clauses)

        clauses = self.drop_batches(clauses)
        clauses = self.drop_individual(clauses)

        self.set_seed('min',clauses)
        if self.gen == 'container':
            maze_gen.generate_mazes([self.params],self.outdir)
        else:
            maze_gen.generate_maze(self.params, self.outdir)
        LOGGER.info("Done!")

    def separate_unsat_core(self,clauses: list):
        core = sp.get_unsat_core(clauses, self.logic)
        LOGGER.debug("Found core %s", core)
        return list(filter(lambda c : c not in core, clauses)), core


    def minimize_maze(self):
        if not 'u' in self.params.keys():
            w, h = self.params['w'], self.params['h']
            self.params.update({'u':'', 'w':1, 'h':1})
            if not self.result_is_err():
                self.params.pop('u')
                self.params.update({'w':w,'h':h})
        
    def get_seed(self):
        if 'storm' in self.params['t']:
            return os.path.join(self.outdir,'smt',str(self.params['r']), 'mutant_%d.smt2' % (self.params['m'] - 1))
        if 'fuzz' in self.params['t'] or 'yinyang' in self.params['t']:
            return os.path.join(self.outdir,'smt',str(self.params['r']), f"mutant_{self.params['m']-1}_{'sat' if self.expected_result == 'error' else 'unsat'}.smt2")
        return self.params['s']

    def drop_batches(self, clauses: list):
        keep_first_half = True
        misses_bug = True
        min_clauses = 1 if self.expected_result == 'error' else 0
        while (len(clauses) > min_clauses) and (misses_bug or not keep_first_half):
            half = len(clauses) // 2
            new_clauses = clauses[:half] if keep_first_half else clauses[half+1:]
            seed = str(half) + ('-first' if keep_first_half else '-second')
            self.set_seed(seed,new_clauses)
            misses_bug = self.result_is_err()
            if misses_bug:
                clauses = new_clauses
                logging.info("Discarded %s half of constraints", 'first' if keep_first_half else 'second')
                keep_first_half = True
            else:
                keep_first_half = not(keep_first_half)
        return clauses

    def drop_individual(self, clauses: list):
        empty_clauses = 0
        for i in range(len(clauses)):
            if len(clauses) == 1 and self.expected_result == 'error':
                break
            commands.run_cmd('mkdir -p %s' % os.path.join(self.outdir,'seeds'))
            pos = i - empty_clauses
            seed = str(len(clauses)) + '-' + str(pos+1)
            clause = clauses.pop(pos)
        
            self.set_seed(seed,clauses)
            misses_bug = self.result_is_err()
            
            if misses_bug:
                empty_clauses += 1
            else:
                clauses.insert(pos, clause) # Reinsert clause if no longer an error
        return clauses

    def result_is_err(self, rm=True):
        docker.run_pa(self.tool,self.variant,self.flags,1, self.params, self.outdir,timeout=self.timeout, gen=self.gen, expected_result=self.expected_result)
        sat = self.is_err()
        if rm:
            commands.run_cmd('rm -r %s' % os.path.join(self.outdir, 'src'))
        return sat

    def set_seed(self, seed: str, clauses: list):
        seed = f"{seed.removesuffix('.smt2')}_{'sat' if self.expected_result == 'error' else 'unsat'}.smt2"
        seed = os.path.join(self.outdir, 'seeds', seed)
        constraints = self.core.union(clauses)
        sp.write_to_file(constraints,self.logic,seed)
        self.params['s'] = seed


    def is_err(self):
        maze = maze_gen.get_maze_names(self.params)[self.params['m'] - (0 if 'keepId' in self.params['t'] else 1)]
        resdir = os.path.join(self.outdir,maze,maze)
        if os.path.isdir(resdir):
            for file in os.listdir(resdir):
                if len(file.split('_')) == 2:
                    LOGGER.info(file)
                    commands.run_cmd('mv %s %s' % (os.path.join(resdir,file), os.path.join(self.outdir,'runs')))
                    commands.run_cmd('rm -r %s' % os.path.join(self.outdir,maze))
                    if self.err in file: 
                        return True
        return False

    def get_params(self, maze, smt_path = ''):
        self.maze = maze.split('/')[-1][:-2] # Cut .c
        self.params= maze_gen.get_params_from_maze(self.maze,smt_path=smt_path)
        return self.params

    def set_fake_params(self):
        transforms = set(filter(lambda t: not ('storm' in t or 'fuzz' in t or 'yinyang' in t), self.params['t'].split('_')))
        if self.expected_result == 'safe':
            transforms.add('unsat')
        self.params['t'] = '_'.join(transforms)
        self.params['t'] = self.params['t'].strip('_')
        if self.params['t'] == '' or self.params['t'] == 'last':
            self.params['t'] = 'keepId'
            self.params['m'] = 0
        else:
            self.params['m'] = 1

def read_mutant(mutant: str):
    file_data = sp.read_file(mutant)
    return list(file_data.clauses), file_data.logic

def find_seed_dir(root: str, seed: str) -> str | None:
    if os.path.isdir(root):
        files = os.listdir(root)
        if seed in files:
            return root
        for file in files:
            res = find_seed_dir(os.path.join(root,file),seed)
            if res is not None:
                return res
    return None
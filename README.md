# Minotaur
Minotaur is a generative black-box fuzzer for software model checkers, based on [Fuzzle](https://github.com/SoftSec-KAIST/Fuzzle) and (optionally) using [STORM](https://github.com/mariachris/storm).

## About
Minotaur uses sat/unsat SMT-Files to generate programs that are unsafe/safe by construction, which can be used to test program anaylzers for soundness/precision issues. 

## Requirements
- Python 3.10 or 3.11
- [Docker](https://docs.docker.com/engine/install/) (or similar)

## Installation
We tested installation on Ubuntu 22.04 and Debian 12. If you're using a different system, you might need to install
the dependencies in a different manner.
```bash
sudo snap install docker
sudo usermod -aG docker $USER
 newgrp docker
./Minotaur/scripts/build_MC_dockers.sh <num_cores>
./Minotaur/scripts/build_experiment_dockers.sh <num_cores>
```
where <num_cores> is the number of cores available for parallel builds (recommended to keep at least two cores free).

Note that the provided dockers build the analyzers under test from source. Building might take up to a few hours and several GBs of memory.
The builds need to download data from remote mirrors, so it can occasionally occur that the build fails because a connection is terminated.
In this case, rerunning the script usually fixes the problem.

### Install python3 dependencies
#### NOTE: if you only want to run tests or experiments, you can skip this step. 

If you want to generate mazes locally or perform minimization, you will need to install the packages from [requirements.txt](requirements.txt)
We recommend using a [virtualenv](https://virtualenv.pypa.io/en/latest/):
```bash
# python3.10 or python3.11
sudo apt install python3-virtualenv
virtualenv --python=/usr/bin/python3.XX venv
source venv/bin/activate
pip install -r Minotaur/requirements.txt
```
If you want to use STORM locally, update the STORM home in the [config file](src/maze_gen/storm/config.py).

# Usage
## Recreating ASE 2024 paper results
For more informations on the provided experiment configurations see [this guide](recreate_results.md) on how to recreate the experiment results. 

## Using Minotaur
### Test Analyzers
Runs are configured via conf.json files located in the [test](test) folder.
To perform a test using the config file test/conf_name.conf.json run 
```bash
python Minotaur --t <conf_name> <outdir>
```
For more info on config files check [config.md](./config.md) and the example config files provided.
Results are written to `summary.csv`; lines ending in `fn` (`fp`) indicate that a soundness (precision) 
issue has been found for the listed parameters.

### Run experiments
Before recreating experiments, build the necessary experiment Dockers. Then run the experiment for a given config similar to starting a test run: 
```bash
./Minotaur/scripts/build_experiment_dockers.sh
python Minotaur --e <experiment_name> <outdir>
```
Experiment configurations are stored in the [experiments](experiments) folder. 

### Generate a specific maze
```
python Minotaur --g {local,container} <outdir> <params...>
```
Will generate the maze + any transformations specified.
`container` indicates that mazes should be generated within a container, which is slower, but works without installing 
the python dependencies. `local` is faster but requires the dependencies. 
For parameter options see [params.md](./params.md).

### Minimize a maze
```
python Minotaur --m <report> <seed-dir> <outdir> {local,container}
```
`<report>` is the line from the `summary.csv` (wrapped in single quotes) corresponding to the test case you want to minimize, e.g.
```
esbmc-bug1,23695,--interval-analysis,,2,1,storm_mc100_dag3,CVE_gen,app12bench_930.smt2,3666,00000.11000,fn
```
for a test that caused a soundness bug in the interval-analysis of tool esbmc-bug1.

The csv contains most of the information required to recreate and minimize the test, you only need to set `<seed-dir>` to tell the minimizer where it should look for the original seed constraint file used in the generation (Minotaur will also search in subdirectories of `<seed-dir>`).

The remaining options are the same as for generation.

### Filter accepted seed files
```bash
python Minotaur --c <seed_dir> <outfile> {sat,unsat}
```
will recursively search for compatible smtfiles for sat/unsat seed generation (=> unsafe/safe programs).
Compatible files will be written to outfile. Files can then be collected, e.g. with `mkdir safe_seeds && for f in $(cat outfile); do cp seed_dir/"$f" safe_seeds; done`.

### Logging
For all tools the logging level can be set via --LEVEL with LEVEL being one of E(rror), W(arning), I(nfo) or D(ebug). E.g. `python3 --t --D conf outdir` runs tests with log-level `DEBUG`.
Note that container outputs are only tracked if the logging level is set to Debug

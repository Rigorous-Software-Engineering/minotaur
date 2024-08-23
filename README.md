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

### Building dockers manually
If you only want to install the analyzers for a specific experiment, 
all necessary Dockerfiles are stored in the [dockers](dockers) folder.
Minotaur expects the images to be tagged as `minotaur-<tool>`,
where `<tool>` is one of the folders in the dockers directory.
You will always need to build the base docker and the generation docker:
```bash
docker build -t minotaur-base Minotaur/dockers/base
docker build -t minotaur-gen Minotaur # only Dockerfile not in ./dockers
```
You will also need dockers for all analyzers mentioned in the `"tool"`
and (if present) `"check_error"` fields of the configuration
file. Note that some tool dockers require their own `base-`build.
Scroll down to the end of the page to see a full list of the dockers
needed for each experiment. 

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



## Dockers required for each experiment
|Experiment|Dockers required|
|---|---|
|*Always*|`minotaur-base`, `minotaur-gen`|
|Per experiment: |
|coverage.conf.json|`minotaur-esbmc-base`, `minotaur-esbmc`, `minotaur-cbmc`, `minotaur-seahorn`|
|recreate1.conf.json|`minotaur-esbmc-base`, `minotaur-2ls`|
|recreate2.conf.json|`minotaur-esbmc-base`, `minotaur-cbmc`|
|recreate3.conf.json|`minotaur-esbmc-base`, `minotaur-cbmc`|
|recreate4.conf.json|`minotaur-cpa-base`, `minotaur-cpa-fixed1`, `minotaur-cpa-bug1`|
|recreate5.conf.json|`minotaur-cpa-base`, `minotaur-cpa-bug2`, `minotaur-cpa-fixed2`|
|recreate6.conf.json|`minotaur-cpa-base`, `minotaur-cpa-bug3`, `minotaur-cpa-fixed3`|
|recreate7.conf.json|`minotaur-cpa-base`, `minotaur-cpa`|
|recreate8.conf.json|`minotaur-cpa-base`, `minotaur-cpa-bug4`|
|recreate9.conf.json|`minotaur-cpa-base`, `minotaur-cpa`|
|recreate10.conf.json|`minotaur-esbmc-base`, `minotaur-esbmc-fixed1`, `minotaur-esbmc-bug1`|
|recreate11.conf.json|`minotaur-esbmc-base`, `minotaur-esbmc-bug2`, `minotaur-esbmc-fixed2`|
|recreate12.conf.json|`minotaur-esbmc-base`, `minotaur-esbmc-bug3`, `minotaur-esbmc-fixed3`|
|recreate13.conf.json|`minotaur-esbmc-base`, `minotaur-esbmc-fixed4`, `minotaur-esbmc-bug4`|
|recreate14.conf.json|`minotaur-esbmc-base`, `minotaur-esbmc`|
|recreate15.conf.json|`minotaur-esbmc-base`, `minotaur-esbmc`|
|recreate16.conf.json|`minotaur-mopsa`|
|recreate17.conf.json|`minotaur-mopsa`|
|recreate18.conf.json|`minotaur-mopsa`|
|recreate19.conf.json|`minotaur-mopsa-bug1`, `minotaur-mopsa-fixed1`|
|recreate20.conf.json|`minotaur-mopsa`|
|recreate21.conf.json|`minotaur-mopsa`|
|recreate22.conf.json|`minotaur-mopsa`|
|recreate23.conf.json|`minotaur-seahorn`|
|recreate24.conf.json|`minotaur-seahorn`|
|recreate25.conf.json|`minotaur-seahorn`|
|recreate26.conf.json|`minotaur-symbiotic`|
|recreate27.conf.json|`minotaur-symbiotic`|
|recreate28.conf.json|`minotaur-ultimate-fixed1`, `minotaur-ultimate-bug1`|
|recreate29.conf.json|`minotaur-ultimate-fixed2`, `minotaur-ultimate-bug2`|
|recreate30.conf.json|`minotaur-ultimate-bug3`, `minotaur-ultimate-fixed3`|
|recreate31.conf.json|`minotaur-ultimate-fixed4`, `minotaur-ultimate-bug4`|
|time_to_bug4.conf.json|`minotaur-cpa-base`, `minotaur-cpa-fixed1`, `minotaur-cpa-bug1`|
|time_to_bug5.conf.json|`minotaur-cpa-base`, `minotaur-cpa-bug2`, `minotaur-cpa-fixed2`|
|time_to_bug6.conf.json|`minotaur-cpa-base`, `minotaur-cpa-bug3`, `minotaur-cpa-fixed3`|
|time_to_bug8.conf.json|`minotaur-cpa-base`, `minotaur-cpa-bug4`, `minotaur-cpa-fixed4`|
|time_to_bug10.conf.json|`minotaur-esbmc-base`, `minotaur-esbmc-fixed1`, `minotaur-esbmc-bug1`|
|time_to_bug11.conf.json|`minotaur-esbmc-base`, `minotaur-esbmc-bug2`, `minotaur-esbmc-fixed2`|
|time_to_bug12.conf.json|`minotaur-esbmc-base`, `minotaur-esbmc-bug3`, `minotaur-esbmc-fixed3`|
|time_to_bug13.conf.json|`minotaur-esbmc-base`, `minotaur-esbmc-fixed4`, `minotaur-esbmc-bug4`|
|time_to_bug19.conf.json|`minotaur-mopsa-bug1`, `minotaur-mopsa-fixed1`|
|time_to_bug21.conf.json|`minotaur-mopsa-fixed2`, `minotaur-mopsa-bug2`|
|time_to_bug28.conf.json|`minotaur-ultimate-fixed1`, `minotaur-ultimate-bug1`|
|time_to_bug29.conf.json|`minotaur-ultimate-fixed2`, `minotaur-ultimate-bug2`|
|time_to_bug30.conf.json|`minotaur-ultimate-bug3`, `minotaur-ultimate-fixed3`|
|time_to_bug31.conf.json|`minotaur-ultimate-fixed4`, `minotaur-ultimate-bug4`|

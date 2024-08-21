## Configuration files
Automated testing and experiments are configured via config.json files. Some examples can be found in the [test](test) and [experiments](experiments) folders.
In particular config files accept the following values
- `workers`: Number of cores to use in parallel
- `memory`: Memory to use per worker
- `duration`: Time to run tools per maze
- `transforms`: Number of transformations per maze
- `batch_size`: How many mazes will be tested before collecting results. Use higher numbers if spawning containers is expensive. 
- `repeats`: Number of batches to generate (-1 to run until cancelled), 
   - Total number of mazes generated = `repeats` * `batch_size`
- `batch_duration` Sets the time before a batch gets killed, specified as the average time a maze should have (i.e. the total time for a batch is batch_duration*batch_size) 
- `maze_gen=['local','container']`: Generate mazes locally one at a time or in parallel in docker
-  `verbosity=['all','bug','summary','bug_only']`: Container output to keep: `all` keeps all, `bug` only for buggy outputs (fn or fp), `summary` only logs results to `summary.csv`, but keeps no output and `bug_only` only logs bugs to `summary.csv`
-  `expected_results=['error','safe',`infer`]`: `error` expects soundness tests, `safe` precision tests, `infer` for mixed tests (with `fuzz` or `yinyang`).
-  `parameters`: Possible values for [generation parameters](parameters.md). Can either be a list of possible values or an object specifiying a `min  and `max` value
    - Transformations (parameter `t`) expects an obejct containing for each transformation their possible values, specified same as other parameters. Please refer to the [list of transformations](params.md#transformations).
- `tools`: Tools to be tested. It is necessary to add an object specifiying a variant (e.g. Taipan/Kojak/etc. for Ultimate). Flags can be set in two ways:
    -  `"toggle"`: A list of flags that are toggled on or off at random.
    -  `"choose"`: An object containing flags of the form `'prefix': [0,'opt1','opt2',...]`. This chooses one of the option and writes it + the prefix. If the option is 0, nothing will be written. E.g. `'--paths ': [0,'fifo','lifo']` will write one of `['','--paths fifo', '--paths lifo']`.
 -  `cov=[0,1]`: Collect coverage data. Currently only supported by ESBMC, CBMC, SeaHorn dockers
 -  `gen_time`: Timeout maze generation after this many seconds
 -  `abort_on_error=[flag1,flag2,...]`: Stop the test if one of the flags is triggered. Mainly useful when attemting to recreate a specific bug
 -  `check-error`: For recreating bugs, specify a fixed version for each buggy tool version container to check if the bug found is solved in the new version.
 -  `use-core`: If >= 0, pin dockers to the selected CPU. Useful for experiments, not recommended for testing. Default: -1  
### Configuring experiments
Experiments essentially consists of multiple test configuratinos run in sequence. How many tests can be specified via the following parameter: 
- `repeats`: This specifies the number of tests to run.
- `avg` Optinally every test can be run multiple times to collect the average time. However times should mostly be mostly deterministic.
- `batches`: As the `repeats` parameter is already reserved, use this to specify the `repeats` for each test.


The total number of tests run is then `repeats`*`average`

All other parameters are the same as for tests, except they can also be a list of the corresponding type.
The i-th experiment will then use the i-th element of the list (modulo the length of the list if there are more repeats than list items). 

If the parameter is not a list it will be kept the same for all tests.

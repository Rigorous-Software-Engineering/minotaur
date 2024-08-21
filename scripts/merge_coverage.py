import os
import sys
import subprocess
for run in sys.argv[1:]:
    out_dir = os.path.join(run, 'cov')
    resfiles = list(os.listdir(out_dir))
    for tool in ["cbmc","esbmc","seahorn"]:
        files = []
        total = 0
        for file in resfiles:
            if tool in file and not 'batches' in file:
                total += 1
                files.append(os.path.join(out_dir,file)) # For some reason filter + lambda does not work for this
                file_string = ' --json-add-tracefile '.join(files)
                outfile = f"{tool}_{total}batches.cov.json"
                tempfile = f"{tool}_{total}temp.cov.json"
                cmd = f"python3 -m gcovr --json-add-tracefile {file_string}  --merge-mode-functions=separate --json {os.path.join(out_dir,tempfile)} --json-summary-pretty > {os.path.join(out_dir, outfile)}"
                print(cmd)
                subprocess.run(args=cmd, shell=True)
                files = [os.path.join(out_dir,tempfile)]

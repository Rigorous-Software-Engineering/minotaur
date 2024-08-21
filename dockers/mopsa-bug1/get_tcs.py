import os, sys

def save_tc(dest_dir, tc_path, start_time, end_time, sig, copy_content=True):
    elapsed_time = end_time - start_time
    if sig == '':
        sig = 'tc'
    name = '%011.5f_%s' % (elapsed_time, sig)
    file_path = os.path.join(dest_dir, name)
    if copy_content:
        os.system('mv %s %s' % (tc_path, file_path))
    else:
        os.system('touch %s' % (file_path))
        os.system('rm %s' % (tc_path))




WORKDIR = '/home/maze/workspace'
OUTDIR = '/home/maze/workspace/outputs'

def main(dest_dir,verbosity,expected_results):
    expected_result_by_maze = {}
    if expected_results.endswith('.txt'):
        with open(expected_results,'r') as results_file:
            for result in results_file.readlines():
                name, res = result.rsplit(' ',1)
                expected_result_by_maze[name] = res.strip()
    # Create destination directory
    os.system('mkdir -p %s' % dest_dir)
    for file in filter(lambda f: 'res' in f, os.listdir(OUTDIR)):
        name = file[3:]
        respath = '%s/%s' %(OUTDIR,file)
        try:
            start_file = os.path.join(WORKDIR, '.start%s' % name)
            start_time = os.path.getmtime(start_file)
            end_file = os.path.join(WORKDIR, '.end%s' % name)
            end_time = os.path.getmtime(end_file)       
            resfile = open(respath, "r").read()
            file_dir = os.path.join(dest_dir,name) 
            os.system('mkdir -p %s' % file_dir)
            expected_result = expected_result_by_maze[name] if expected_results.endswith('.txt') else expected_results 
        except Exception as e:
            print("NOTE: Failed to parse file %s: %s" % (file, str(e)))
            continue
        flag = ''
        if ('⚠' in resfile):
            flag = 'wa-'
        # True positives
        if ('Assertion failure' in resfile):
            save_tc(file_dir, respath, start_time, end_time,flag + ('tp' if expected_result == 'error' else 'fp'))
        # False negatives
        elif ('No alarm' in resfile):
            save_tc(file_dir, respath, start_time, end_time, flag + ('fn' if expected_result == 'error' else 'tn'))
        elif ('panic: ' in resfile):
            save_tc(file_dir, respath, start_time, end_time, flag + 'er', copy_content = verbosity in ('error','all'))
        # Timeout
        else: 
            save_tc(file_dir, respath, start_time, end_time, flag + 'to', copy_content = verbosity == 'all')

if __name__ == '__main__':
    dest_dir = sys.argv[1]    
    expected_results = sys.argv[3]
    verbosity = sys.argv[2]
    main(dest_dir,verbosity,expected_results)

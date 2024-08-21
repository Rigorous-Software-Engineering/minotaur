from numpy import NaN, average
import pandas
import sys
import os
run_directory = sys.argv[1]
df = pandas.read_csv(os.path.join(run_directory,'times'), header='infer')
num_tests = int(sys.argv[2])
total_runs = len(df.iloc[:,1])
flag = sys.argv[3]

for test_id in range(num_tests):
    tool_times = []
    fn_times = []
    found = [False] * total_runs
    for run in range(test_id, total_runs, num_tests):
        summary = pandas.read_csv(os.path.join(run_directory, f'run{run}_{0}','summary.csv'), header='infer')
        tool_times.append(sum(filter(lambda r: isinstance(r, float),summary['runtime'][::])))
        if len(summary['status']) > 0 and summary['status'][len(summary['status'])-1] == flag:
            found[run] = True
            fn_times.append(summary['runtime'][len(summary['status'])-1])
            tool_times.append(sum(map(float,filter(lambda t: t!='notFound',summary['runtime'][::]))))
    avg = NaN if len(df.iloc[found,1]) == 0 else average(df.iloc[found,1])
    avg_tool_time = NaN if len(tool_times) == 0 else average(tool_times)

    print(f"Test {test_id}:\tTotal time {avg:.2f},\t Tool time {avg_tool_time:.0f},\tPA% = {100*avg_tool_time / avg:.1f}\t found {sum(found)}/5, Times for {flag}: {NaN if len(fn_times) == 0 else fn_times}")

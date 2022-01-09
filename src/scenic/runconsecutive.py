
import subprocess
import sys
import json

maps = ['zalafullcrop']
configurations = ['2actors']
scene_ids = range(10) # TODO 10
approach = 'nsga'
iterations = range(1,2)

global_timeout = 30
verbosity = 0
save = True

resWS = 'measurements/results'
restart_times = [90]

for m in maps:
    for config in configurations:
        for iter in iterations:
            for restart_time in restart_times:
                global_summary = {'map':m, 'config':config, 'results':[]}
                cur_timeout = global_timeout
                prev_total_time = 0
                for i in scene_ids:
                    pathToSrc = f'{m}/{config}/{i}-0/d-{approach}'
                    pathToTgtDir = f'{m}/consecutive/{config}/iter{iter}/restart{restart_time}'
                    pathToTgt = f'{pathToTgtDir}/{i}'
                    command = ['scenic', '-b']
                    command.extend(['--count', '1'])
                    command.extend(['-v', str(verbosity)])
                    if approach == 'nsga':
                        command.extend(['-p', 'nsga', 'True'])
                        command.extend(['-p', 'nsga-NumSols', 'measurement'])
                    command.extend(['-p', 'timeout', str(cur_timeout)])
                    command.extend(['-p', 'outputWS', resWS])
                    command.extend(['-p', 'outputDir', pathToTgt])
                    command.extend(['-p', 'saveImgs', str(save)])
                    command.extend(['-p', 'saveFiles', str(save)])
                    command.extend(['-p', 'saveStats', str(save)])
                    command.extend(['-p', 'map', f'maps/{m}.xodr'])
                    command.extend(['-p', 'restart-time', str(restart_time)])
                    command.append(f'measurements/data/{pathToSrc}.scenic')
                    print(pathToTgt)

                    p = subprocess.Popen(command, stderr=sys.stderr, stdout=sys.stdout, shell=True)
                    # Keep below for server
                    # p = subprocess.Popen(command, stderr=sys.stderr, stdout=sys.stdout)
                    p.wait()

                    # Get timeout info
                    meas_path = f'{resWS}/{pathToTgt}/_measurementstats.json'
                    with open(meas_path) as f:
                        meas_data = json.load(f)
                    prev_timeout = meas_data['results'][0]['time']
                    prev_success = meas_data['results'][0]['success']
                    num_restarts = len(meas_data['results'][0]['restarts'])
                    prev_total_time += prev_timeout

                    # save res
                    summary_path = f'{resWS}/{pathToTgtDir}/summary.json'
                    results = {'scene_id':i, 'success':prev_success, 'time':prev_timeout, 'num-restarts':num_restarts, 'total_time':prev_total_time}
                    global_summary['results'].append(results)
                    with open(summary_path, 'w') as outfile:
                        json.dump(global_summary, outfile, indent=4)
                    print(f'  Saved summary at    {summary_path}')

                    # prep next timeout
                    cur_timeout = cur_timeout - prev_timeout
                    if cur_timeout < 0.001:
                        break

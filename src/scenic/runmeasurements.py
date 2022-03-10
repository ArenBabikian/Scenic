
import subprocess
import sys
import os

short=False

if short:
    maps = ['tram05', 'town02', 'zalaFullcrop']
    configurations = ['2actors', '3actors', '4actors']
    scene_ids = range(10) # TODO 10
    approaches = ['sc1', 'sc2', 'sc3', 'nsga']
    num_iterations = 10
    timeout = [600, 600, 600, 600] # 10min
else:
    #scale
    maps = ['zalaFullcrop']
    configurations = ['7actors'] # 4 5 6 7
    scene_ids = range(5)
    approaches = ['nsga']
    num_iterations = 5
    timeout = [7200] # 2h

verbosity = 0
save = True

for config in configurations:
    for m in maps:
        for i in scene_ids:
            for a_ind in range(len(approaches)):
                approach = approaches[a_ind]
                pathToFile = f'{m}/{config}/{i}-0/d-{approach}'
                command = ['scenic', '-b']
                command.extend(['--count', str(num_iterations)])
                command.extend(['-v', str(verbosity)])
                if approach == 'nsga':
                    command.extend(['-p', 'nsga', 'True'])
                    command.extend(['-p', 'nsga-NumSols', 'measurement'])
                command.extend(['-p', 'timeout', str(timeout[a_ind])])
                command.extend(['-p', 'outputWS', 'measurements/results'])
                command.extend(['-p', 'outputDir', pathToFile])
                command.extend(['-p', 'saveImgs', str(save)])
                command.extend(['-p', 'saveFiles', str(save)])
                command.extend(['-p', 'saveStats', str(save)])
                command.extend(['-p', 'restart-time', str(-1)])
                command.append(f'measurements/data/{pathToFile}.scenic')
                print(pathToFile)

                # p = subprocess.Popen(command, stderr=sys.stderr, stdout=sys.stdout, shell=True)
                # Keep below for server
                p = subprocess.Popen(command, stderr=sys.stderr, stdout=sys.stdout)
                p.wait()


import subprocess
import sys
import os

maps = ['tram05', 'town02']
configurations = ['5actors']
scene_ids = range(6, 20) #20
approaches = ['nsga']

num_iterations = 3 #10
timeout = [1800]
verbosity = 0
save = True

for i in scene_ids:
    for m in maps:
        for config in configurations:
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
                command.extend(['-p', 'saveStats', str(save)])
                command.append(f'measurements/data/{pathToFile}.scenic')
                print(pathToFile)

                p = subprocess.Popen(command, stderr=sys.stderr, stdout=sys.stdout, shell=True)
                p.wait()
            




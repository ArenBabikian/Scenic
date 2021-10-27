
import subprocess
import sys
import os

maps = ['tram05']
configurations = ['3actors', '4actors', '2actors']
num_scenes = 20 #20
approaches = ['sc1', 'sc2', 'sc3', 'nsga']

num_iterations = 5 #10
timeout = 60
verbosity = 0

for m in maps:
    for config in configurations:
        for i in range(num_scenes):
            for approach in approaches:
                pathToFile = f'{m}/{config}/{i}-0/d-{approach}'
                command = ['scenic']
                command.extend(['--count', str(num_iterations)])
                command.extend(['-v', str(verbosity)])
                if approach == 'nsga':
                    command.extend(['-p', 'nsga', 'True'])
                    command.extend(['-p', 'nsga-NumSols', '1'])
                command.extend(['-p', 'timeout', str(timeout)])
                command.extend(['-p', 'outputWS', 'measurements/results'])
                command.extend(['-p', 'outputDir', pathToFile])
                command.extend(['-p', 'saveImgs', 'True'])
                command.extend(['-p', 'saveStats', 'True'])
                command.append(f'measurements/data/{pathToFile}.scenic')
                print(pathToFile)

                p = subprocess.Popen(command, stderr=sys.stderr, stdout=sys.stdout, shell=True)
                p.wait()
            




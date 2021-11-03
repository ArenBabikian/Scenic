
import subprocess
import sys
import os

maps = ['tram05']
configurations = ['3actors']
scene_ids = range(5) #20
approaches = ['nsga']
# TODO range(5, 20), 'nsga', 5 iter, [2actors, 3actors]

# TODO range (17, 20), [sc1, sc2, sc3], 5 iter, 300 timeout
# TODO 16, sc3, 5 iter, 300 timeout
# TODO everything, 4actors

num_iterations = 5 #10
timeout = 300
verbosity = 0

for m in maps:
    for config in configurations:
        for i in scene_ids:
            for approach in approaches:
                pathToFile = f'{m}/{config}/{i}-0/d-{approach}'
                command = ['scenic', '-b']
                command.extend(['--count', str(num_iterations)])
                command.extend(['-v', str(verbosity)])
                if approach == 'nsga':
                    command.extend(['-p', 'nsga', 'True'])
                    command.extend(['-p', 'nsga-NumSols', 'measurement'])
                command.extend(['-p', 'timeout', str(timeout)])
                command.extend(['-p', 'outputWS', 'measurements/results'])
                command.extend(['-p', 'outputDir', pathToFile])
                command.extend(['-p', 'saveImgs', 'True'])
                command.extend(['-p', 'saveStats', 'True'])
                command.append(f'measurements/data/{pathToFile}.scenic')
                print(pathToFile)

                p = subprocess.Popen(command, stderr=sys.stderr, stdout=sys.stdout, shell=True)
                p.wait()
            




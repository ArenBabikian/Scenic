
import subprocess
import sys
import os

maps = ['tram05', 'town02']
configurations = ['2actors', '3actors', '4actors']
scene_ids = range(10) # TODO 10
approaches = ['sc1', 'sc2', 'sc3', 'nsga']

# TODO range (17, 20), [sc1, sc2, sc3], 5 iter, 300 timeout
# TODO 16, sc3, 5 iter, 300 timeout
# TODO 4actors, range (10, 20), [nsga], 5 iter, 3600 timeout
# TODO 4actors, range (10, 20), [sci, sc2, sc3], 5 iter, 300 timeout

num_iterations = 10 # TODO 10
timeout = [600, 600, 600, 600]
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
                command.extend(['-p', 'saveStats', str(save)])
                command.append(f'measurements/data/{pathToFile}.scenic')
                print(pathToFile)

                # p = subprocess.Popen(command, stderr=sys.stderr, stdout=sys.stdout, shell=True)
                # Keep below for server
                p = subprocess.Popen(command, stderr=sys.stderr, stdout=sys.stdout)
                p.wait()

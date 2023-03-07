
import subprocess
import sys
import os

setting = "short" # short, scale, constraints

if setting == "short":
    maps = ['tram05', 'town02', 'zalaFullcrop']
    configurations = ['2actors', '3actors', '4actors']
    scene_ids = range(10)
    approaches = ['sc1', 'sc2', 'sc3', 'nsga']
    num_iterations = 10
    timeout = [600, 600, 600, 600] # 10min
elif setting == "scale":
    maps = ['zalaFullcrop']
    configurations = ['7actors'] # 4 5 6 7
    scene_ids = range(5)
    approaches = ['nsga']
    num_iterations = 5
    timeout = [7200] # 2h
elif setting == "constraints":
    maps = ['zalaFullcrop']
    # configurations = ['cons/none', 'cons/r', 'cons/rc', 'cons/rcv', 'cons/rcvd'] # TODO add 'cons/rcvdp'
    configurations = ['cons/rcp', 'cons/rcpd', 'cons/rcpdv']
    scene_ids = range(10)
    approaches = ['nsga']
    num_iterations = 10
    timeout = [600] # 10min
else:
    exit()

verbosity = 0
save = True

for config in configurations:
    for m in maps:
        for i in scene_ids:
            for a_ind in range(len(approaches)):
                approach = approaches[a_ind]
                if setting != "constraints":
                    pathToFile = f'{m}/{config}/{i}-0/d-{approach}'
                else:
                    pathToFile = f'{m}/{config}/{i}'
                fullPathToFile = f'measurements/data/{pathToFile}.scenic'
                if not os.path.exists(fullPathToFile):
                    print(f'File not found at: {fullPathToFile}')
                    continue
                command = ['scenic', '-b']
                command.extend(['--count', str(num_iterations)])
                command.extend(['-v', str(verbosity)])
                if approach == 'nsga':
                    command.extend(['-p', 'evol', 'True'])
                    command.extend(['-p', 'evol-algo', 'nsga'])
                    command.extend(['-p', 'evol-NumSols', 'measurement'])
                command.extend(['-p', 'timeout', str(timeout[a_ind])])
                command.extend(['-p', 'outputWS', 'measurements/results'])
                command.extend(['-p', 'outputDir', pathToFile])
                command.extend(['-p', 'saveImgs', str(save)])
                command.extend(['-p', 'saveFiles', str(save)])
                command.extend(['-p', 'saveStats', str(save)])
                command.extend(['-p', 'evol-restart-time', str(-1)])
                command.append(fullPathToFile)
                print(fullPathToFile)

                # p = subprocess.Popen(command, stderr=sys.stderr, stdout=sys.stdout, shell=True)
                # Keep below for server
                p = subprocess.Popen(command, stderr=sys.stderr, stdout=sys.stdout)
                p.wait()

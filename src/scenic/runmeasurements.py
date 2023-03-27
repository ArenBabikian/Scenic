
import subprocess
import sys
import os

setting = "testing" # short, scale, constraints, evol, testing, meas-test

if setting == "short":
    maps = ['tram05', 'town02', 'zalaFullcrop']
    configurations = ['2actors', '3actors', '4actors']
    scene_ids = range(10)
    approaches = ['sc1', 'sc2', 'sc3', 'nsga']
    num_iterations = 10
    timeout = [600, 600, 600, 600] # 10min
    evol_approaches = [('nsga2', 'categories')]
    evol_history = 'none'
elif setting == "scale":
    maps = ['zalaFullcrop']
    configurations = ['7actors'] # 4 5 6 7
    scene_ids = range(5)
    approaches = ['nsga']
    num_iterations = 5
    timeout = [7200] # 2h
    evol_approaches = [('nsga2', 'categories')]
    evol_history = 'none'
elif setting == "constraints":
    maps = ['zalaFullcrop']
    # configurations = ['cons/none', 'cons/r', 'cons/rc', 'cons/rcv', 'cons/rcvd'] # TODO add 'cons/rcvdp'
    configurations = ['cons/rcp', 'cons/rcpd', 'cons/rcpdv']
    scene_ids = range(10)
    approaches = ['nsga']
    num_iterations = 10
    timeout = [600] # 10min
    evol_approaches = [('nsga2', 'categories')]
    evol_history = 'none'
elif setting == "evol":
    maps = ['tram05']
    configurations = ['2actors', '3actors', '4actors']
    scene_ids = range(10)
    approaches = ['nsga']
    num_iterations = 10
    timeout = [600] # 10min
    evol_approaches = [('nsga3', 'categImpo'),
                       ('nsga2', 'importance'),
                       ('nsga3', 'categories'),
                       ('nsga2', 'actors'),
                       ('nsga3', 'none'),
                       ('ga', 'one'),
                       ('nsga2', 'categImpo'),
                       ('nsga3', 'actors')]
    evol_history = 'shallow'
elif setting == "testing":
    maps = ['tram05']
    configurations = ['3actors']
    scene_ids = range(2)
    approaches = ['nsga']
    num_iterations = 2
    timeout = [30]
    evol_approaches = [('nsga3', 'categImpo'),
                       ('nsga2', 'importance'),
                       ('ga', 'one')]
    evol_history = 'shallow'
elif setting == "meas-test":
    maps = ['tram05']
    configurations = ['3actors']
    scene_ids = range(2, 5)
    approaches = ['nsga']
    num_iterations = 5
    timeout = [45]
    evol_approaches = [('nsga3', 'categImpo'),
                       ('nsga2', 'importance'),
                       ('ga', 'one')]
    evol_history = 'shallow'
else:
    exit()

verbosity = 0
save = True
isWindows = True

for evol_algo, evol_obj in evol_approaches:
    for m in maps:
        for config in configurations:
            for i in scene_ids:
                for a_ind, approach in enumerate(approaches):
                    if setting != "constraints":
                        pathToFile = f'{m}/{config}/{i}-0/d-{approach}'
                    else:
                        pathToFile = f'{m}/{config}/{i}'
                    fullPathToFile = f'measurements/data/{pathToFile}.scenic'
                    saveDir = f'{pathToFile}/{evol_algo}-{evol_obj}'
                    if not os.path.exists(fullPathToFile):
                        print(f'File not found at: {fullPathToFile}')
                        continue
                    command = ['scenic', '-b']
                    command.extend(['--count', str(num_iterations)])
                    command.extend(['-v', str(verbosity)])
                    if approach == 'nsga':
                        command.extend(['-p', 'evol', 'True'])
                        command.extend(['-p', 'evol-algo', evol_algo])
                        command.extend(['-p', 'evol-obj', evol_obj])
                        command.extend(['-p', 'evol-NumSols', 'measurement'])
                        command.extend(['-p', 'evol-history', evol_history])
                    command.extend(['-p', 'timeout', str(timeout[a_ind])])
                    command.extend(['-p', 'outputWS', 'measurements/results'])
                    command.extend(['-p', 'outputDir', saveDir])
                    command.extend(['-p', 'saveImgs', str(save)])
                    command.extend(['-p', 'saveFiles', str(save)])
                    command.extend(['-p', 'saveStats', str(save)])
                    command.extend(['-p', 'evol-restart-time', str(-1)])
                    command.extend(['-p', 'map', f'maps/{m}.xodr'])
                    command.append(fullPathToFile)
                    print(f'{fullPathToFile}: ({evol_algo}, {evol_obj})')

                    if isWindows:
                        p = subprocess.Popen(command, stderr=sys.stderr, stdout=sys.stdout, shell=True)
                    else:
                        p = subprocess.Popen(command, stderr=sys.stderr, stdout=sys.stdout)
                    p.wait()

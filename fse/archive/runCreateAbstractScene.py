
import subprocess
import sys
import os

# Problem configuration
maps = {'town05':[207, 53]
        } # zalaFullcrop
configurations = ['2actorsDyn'] # 3actorsDyn

# Parameters
num_scenes = 2
verbosity = 0
timeout = 600

for config in configurations:
    for m in maps:
        for intersection in maps[m]:
            command = ['poetry', 'run', 'scenic']
            command.extend(['-b'])
            command.extend(['-v', str(verbosity)])
            command.extend(['--count', str(num_scenes)])
            command.extend(['-p', 'timeout', str(timeout)])
            command.extend(['-p', 'outputWS', 'fse/data'])
            command.extend(['-p', 'outputDir', f'{m}/{config}/{intersection}'])

            command.extend(['-p', 'evol', 'True'])
            command.extend(['-p', 'evol-algo', 'nsga2'])
            command.extend(['-p', 'evol-obj', 'actors'])
            command.extend(['-p', 'evol-NumSols', 'measurement'])
            command.extend(['-p', 'evol-restart-time', '-1'])
            command.extend(['-p', 'evol-history', 'shallow'])
            command.extend(['-p', 'no-validation', 'True'])

            command.extend(['-p', 'getAbsScene', 'evol'])
            command.extend(['-p', 'intersectiontesting', f'{intersection}'])

            command.extend(['-p', 'saveImgs', 'True'])
            command.extend(['-p', 'saveFiles', 'True'])
            command.extend(['-p', 'savePaths', 'True'])

            command.extend(['-p', 'map', f'maps/{m}.xodr'])
            command.append(f'fse/config/{config}.scenic')

            # p = subprocess.Popen(command, stderr=sys.stderr, stdout=sys.stdout, shell=True)
            # Keep below for server
            p = subprocess.Popen(command, stderr=sys.stderr, stdout=sys.stdout)
            
            p.wait()
            print()

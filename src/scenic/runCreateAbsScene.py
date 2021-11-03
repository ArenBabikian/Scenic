
import subprocess
import sys
import os

maps = ['tram05']
configurations = ['2actors', '3actors', '4actors']
num_scenes = 20
verbosity = 0

for m in maps:
    for config in configurations:
        command = ['scenic']
        command.extend(['--count', str(num_scenes)])
        command.extend(['-v', str(verbosity)])
        command.extend(['-p', 'nsga', 'False'])
        command.extend(['-p', 'getAbsScene', 'True'])
        command.extend(['-p', 'outputWS', 'measurements/data'])
        command.extend(['-p', 'outputDir', f'{m}/{config}'])
        command.extend(['-p', 'saveImgs', 'True'])
        command.extend(['-p', 'saveFiles', 'True'])
        command.extend(['-p', 'map', f'../maps/{m}.xodr'])
        command.append(f'measurements/config/{config}.scenic')

        p = subprocess.Popen(command, stderr=sys.stderr, stdout=sys.stdout, shell=True)
        p.wait()
            




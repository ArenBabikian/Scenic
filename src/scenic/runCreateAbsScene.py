
import subprocess
import sys
import os

maps = ['tram05', 'town02']
configurations = ['2actors', '3actors', '4actors']
num_scenes = 10
verbosity = 0
timeout = 60

for config in configurations:
    for m in maps:
        command = ['scenic']
        command.extend(['--count', str(num_scenes)])
        command.extend(['-v', str(verbosity)])
        command.extend(['-p', 'nsga', 'False'])
        command.extend(['-p', 'getAbsScene', 'True'])
        command.extend(['-p', 'timeout', str(timeout)])
        command.extend(['-p', 'outputWS', 'measurements/data'])
        command.extend(['-p', 'outputDir', f'{m}/{config}'])
        command.extend(['-p', 'saveImgs', 'True'])
        command.extend(['-p', 'saveFiles', 'True'])
        command.extend(['-p', 'map', f'maps/{m}.xodr'])
        command.append(f'measurements/config/{config}.scenic')

        # p = subprocess.Popen(command, stderr=sys.stderr, stdout=sys.stdout, shell=True)
        # Keep below for server
        p = subprocess.Popen(command, stderr=sys.stderr, stdout=sys.stdout)
        
        p.wait()

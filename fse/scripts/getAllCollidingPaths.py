import subprocess
import sys

intersections = {'town05':[207, 53]
        } # zalaFullcrop

actor_configs = [1, 2, 3, 4]

for m in intersections:

    for intersection in intersections[m]:

        for config in actor_configs:
            command = ['poetry', 'run', 'scenic']
            command.extend(['-b'])
            # command.extend(['-v', str(verbosity)])
            command.extend(['-p', 'outputWS', 'fse/data'])
            command.extend(['-p', 'outputDir', f'{m}-{intersection}/{config}actors/'])

            # command.extend(['-p', 'no-validation', 'True'])

            # command.extend(['-p', 'saveImgs', 'True'])
            # command.extend(['-p', 'saveFiles', 'True'])
            # command.extend(['-p', 'savePaths', 'True'])

            command.extend(['-p', 'static-analysis', 'True'])
            command.extend(['-p', 'static-num-actors', str(config)]) # TODO This may be removed down the line
            command.extend(['-p', 'intersectiontesting', f'{intersection}'])

            command.extend(['-p', 'map', f'maps/{m}.xodr'])
            command.append(f'fse/config/dummy{config}.scenic')
            p = subprocess.Popen(command, stderr=sys.stderr, stdout=sys.stdout)
            
            p.wait()
            print()
            exit()
            


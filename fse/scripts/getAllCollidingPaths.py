import subprocess
import sys

intersections = {'town05':[2240],
                 'town07':[169],
                 'tram05-mod':[176]}
# 'town05':[207] # Original one where testing was done

actor_configs = [1, 2, 3, 4]

view_im, view_path = True, True
# view_im, view_path = False, False

for m in intersections:

    for intersection in intersections[m]:

        for config in actor_configs:
            command = ['poetry', 'run', 'scenic']
            command.extend(['-b'])
            # command.extend(['-v', str(verbosity)])
            command.extend(['-p', 'outputWS', 'fse/data'])
            command.extend(['-p', 'outputDir', f'{m}-{intersection}/{config}actors/'])

            # command.extend(['-p', 'no-validation', 'True'])

            command.extend(['-p', 'static-analysis', 'True'])
            command.extend(['-p', 'static-num-actors', str(config)]) # TODO This may be removed down the line
            command.extend(['-p', 'intersectiontesting', f'{intersection}'])
            
            command.extend(['-p', 'viewImgs', str(view_im)])
            command.extend(['-p', 'showPaths', str(view_path)])

            command.extend(['-p', 'map', f'maps/{m}.xodr'])
            command.append(f'fse/config/dummy{config}.scenic')
            p = subprocess.Popen(command, stderr=sys.stderr, stdout=sys.stdout)
            
            p.wait()
            print()

            


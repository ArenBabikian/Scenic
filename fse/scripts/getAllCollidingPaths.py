import subprocess
import sys

intersections = {'town05':[2240],
                 'town07':[169],
                 'tram05-mod':[176]}
intersections = {'town05':[2240]} # OFFICIAL: Done
intersections = {'town04':[916]} # Standard, 4-way. Residential. GOOD
# intersections = {'town07':[918]} # Weird, 3-way. Rural, trees. GOOD

# NOTE:
# 'town05':[207] # Original one where testing was done
# intersections = {'town03':[861]} # Weird, 5-way intersection. NOT IMPLEMENTED
# intersections = {'tram05-mod':[176]} # Standard, 4-way. NOT IMPLEMENTED
# intersections = {'town04':[1368]} # Weird, Highway Entry. PROBLEM:  Too Big (13, 54, 112, 148)
# intersections = {'town07':[169]} # Standard, 4-way. Simulationn Issue
# intersections = {'town07':[68]} # Weird, 4-way intersection. NOT SELECTED
# intersections = {'town04':[1452]} # Standard, 4-way. Residential. Scenery issues

actor_configs = [1, 2, 3, 4]
# actor_configs = [2]

view_im, view_path = True, True
# view_im, view_path = False, False
save_path = True
# save_path = False

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
            command.extend(['-p', 'intersectiontesting', f'{intersection}'])
            
            command.extend(['-p', 'viewImgs', str(view_im)])
            command.extend(['-p', 'showPaths', str(view_path)])
            command.extend(['-p', 'savePaths', str(save_path)])

            command.extend(['-p', 'map', f'maps/{m}.xodr'])
            command.append(f'fse/config/dummy{config}.scenic')
            p = subprocess.Popen(command, stderr=sys.stderr, stdout=sys.stdout)
            
            p.wait()
            print()

            


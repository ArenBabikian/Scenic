
import subprocess
import sys
import os

setting = "default" # short, scale, constraints, evol, testing, meas-test

if setting == "default":
    maps = ['tram05'] # ['tram05', 'town02', 'zalaFullcrop']
    configurations = ['4actors', '3actors', '2actors']
    scene_ids = range(10) # FOR
    conc_ids = range(10) # FOR

    num_scenes_per_input_which_is_supposed_to_be_an_exact_scenario = 1
    num_abstract_dynamic_scenes = 5
    num_dynamic_conretizations = 3
    num_simulations = 1
    num_frames = 2500
else:
    exit()

verbosity = 0
save = True
render = 0


# for evol_algo, evol_obj in evol_approaches:
for m in maps:
    for config in configurations:
        for i_abs in scene_ids:
            for i_con in conc_ids:

                approach = 'd-nsga'
                evol_algo = 'nsga2-actors' 
                pathToFile = f'{m}/{config}/{i_abs}-0/{approach}/{evol_algo}/{i_con}-0'
                # NOTE: Input is a single exact scenic file from a specifoc concretization

                fullPathToFile = f'docker/{pathToFile}/exact.scenic'
                if not os.path.exists(fullPathToFile):
                    print(f'File not found at: {fullPathToFile}')
                    continue

                command = ['scenic', '-b']
                command.extend(['-v', str(verbosity)])
                command.extend(['--count', str(num_scenes_per_input_which_is_supposed_to_be_an_exact_scenario)])
                command.extend(['-p', 'evol', 'False'])
                command.extend(['-p', 'no-validation', 'True'])

                command.extend(['-S', '--model', 'scenic.simulators.carla.model'])
                command.extend(['--time', str(num_frames)]) # number of frames
                command.extend(['-p', 'sim-numdynconcs', str(num_dynamic_conretizations)])
                command.extend(['-p', 'sim-numabssce', str(num_abstract_dynamic_scenes)])
                command.extend(['-p', 'sim-numSims', str(num_simulations)])
                command.extend(['-p', 'sim-extend', 'True'])

                command.extend(['-p', 'sim-saveStats', str(save)])
                command.extend(['-p', 'outputWS', 'measurements/results-sim'])
                command.extend(['-p', 'outputDir', pathToFile])
                # command.extend(['-p', 'sim-imDir', 'PATH'])

                command.extend(['-p', 'render', str(render)])
                command.extend(['-p', 'map', f'maps/{m}.xodr'])

                command.append(fullPathToFile)
                print(f'{fullPathToFile}')

                p = subprocess.Popen(command, stderr=sys.stderr, stdout=sys.stdout, shell=True) # sheel-False for Linux
                p.wait()
                # exit()

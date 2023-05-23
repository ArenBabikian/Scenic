
import subprocess
import sys
import os

setting = "default" # short, scale, constraints, evol, testing, meas-test

# GLOBAL
# maps = ['town02']
# maps = ['zalaFullcrop']
maps = ['tram05'] # ['tram05', 'town02', 'zalaFullcrop']
num_frames = 1500
verbosity = 0
save = True


spec_dir = 'examples/dynamics'
res_path = 'meas-sim/results'
specs = [
    # {'filename':'test0', 'evol':'True', 'no-validation':'True', 'count':'1'},
    # {'filename':'testExact', 'evol':'False', 'no-validation':'True', 'conc_count':'1', 'render':'1'},
    # {'filename':'testAbstractSimple', 'evol':'False', 'no-validation':'True', 'conc_count':'1', 'render':'1', 'rand-beh':'True'},
    # {'filename':'testAbsDyn', 'evol':'False', 'no-validation':'True', 'conc_count':'1', 'render':'1', 'rand-beh':'False'},
    # {'filename':'testAbsDynBASIC', 'evol':'False', 'no-validation':'True', 'conc_count':'1', 'render':'1', 'rand-beh':'False'}
    # {'filename':'testAbsDyn2actors', 'evol':'True', 'no-validation':'False', 'conc_count':'1', 'render':'1', 'rand-beh':'False'},
    # {'filename':'testAbsDyn2actorsSimple', 'evol':'True', 'no-validation':'False', 'conc_count':'10', 'render':'1', 'rand-beh':'False'},
    # {'filename':'good/abstract', 'evol':'True', 'no-validation':'False', 'conc_count':'10', 'render':'1', 'rand-beh':'False'},
    {'filename':'exact_test', 'evol':'False', 'no-validation':'True', 'conc_count':'1', 'render':'1', 'rand-beh':'False'}
]
#TODO add support for count > 1
    
num_scenes_per_input_which_is_supposed_to_be_an_exact_scenario = 1
num_abstract_dynamic_scenes = 1
num_dynamic_conretizations = 1
num_simulations = 1


for m in maps:
    for spec in specs:

        # NOTE: ARCHIVE: Input is a single exact scenic file from a specifoc concretization

        full_res_path = f'{m}'
        fullPathToFile = f'{spec_dir}/{spec["filename"]}.scenic'
        if not os.path.exists(fullPathToFile):
            print(f'File not found at: {fullPathToFile}')
            continue

        command = ['scenic', '-b']
        command.extend(['-v', str(verbosity)])

        # LEVELS OF ABSTRACTION
        command.extend(['--count', spec['conc_count']])
        command.extend(['-p', 'sim-n-absScenes', str(num_abstract_dynamic_scenes)])
        command.extend(['-p', 'sim-n-concretizations', str(num_dynamic_conretizations)])
        command.extend(['-p', 'sim-n-sims', str(num_simulations)])

        # EVOL
        command.extend(['-p', 'evol', spec['evol']])
        command.extend(['-p', 'evol-algo', 'nsga2'])
        command.extend(['-p', 'evol-obj', 'actors'])
        command.extend(['-p', 'evol-NumSols', 'measurement'])
        command.extend(['-p', 'evol-history', 'shallow'])
        
        # SIMULATION
        command.extend(['-S', '--model', 'scenic.simulators.carla.model'])
        command.extend(['--time', str(num_frames)]) # number of frames
        command.extend(['-p', 'sim-extend', spec['rand-beh']])
        command.extend(['-p', 'render', spec['render']])
        command.extend(['-p', 'no-validation', spec['no-validation']])
        command.extend(['-p', 'sim-imDir', f'{res_path}/images2'])

        # SAVE
        command.extend(['-p', 'outputWS', res_path])
        command.extend(['-p', 'outputDir', m])

        command.extend(['-p', 'sim-saveStats', str(save)])
        # command.extend(['-p', 'viewImgs', str(save)])
        command.extend(['-p', 'saveImgs', str(save)])
        command.extend(['-p', 'saveFiles', str(save)])
        command.extend(['-p', 'saveStats', str(save)])

        command.extend(['-p', 'map', f'maps/{m}.xodr'])
        if m == 'town02':
            command.extend(['-p', 'carla_map', 'Town02'])

        command.append(fullPathToFile)
        print(f'{fullPathToFile}')

        p = subprocess.Popen(command, stderr=sys.stderr, stdout=sys.stdout, shell=True) # sheel-False for Linux
        p.wait()

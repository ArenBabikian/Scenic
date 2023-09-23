
### Top-level functionality of the scenic package as a script:
### load a scenario and generate scenes in an infinite loop.

import sys
import time
import argparse
import random
import os
from datetime import datetime
from pathlib import Path
import json
import gc
import scenic.core.printer.printer as printer
from scenic.core.static_analysis.static_analysis_util import doStaticAnalysis


if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata

import scenic.syntax.translator as translator
import scenic.core.errors as errors
from scenic.core.simulators import SimulationCreationError
import scenic.core.evol.dyn_utils as dyn_util

parser = argparse.ArgumentParser(prog='scenic', add_help=False,
                                 usage='scenic [-h | --help] [options] FILE [options]',
                                 description='Sample from a Scenic scenario, optionally '
                                             'running dynamic simulations.')

mainOptions = parser.add_argument_group('main options')
mainOptions.add_argument('-S', '--simulate', action='store_true',
                         help='run dynamic simulations from scenes '
                              'instead of simply showing diagrams of scenes')
mainOptions.add_argument('-s', '--seed', help='random seed', type=int)
mainOptions.add_argument('-v', '--verbosity', help='verbosity level (default 1)',
                         type=int, choices=(0, 1, 2, 3), default=1)
mainOptions.add_argument('-p', '--param', help='override a global parameter',
                         nargs=2, default=[], action='append', metavar=('PARAM', 'VALUE'))
mainOptions.add_argument('-m', '--model', help='specify a Scenic world model', default=None)
mainOptions.add_argument('--scenario', default=None,
                         help='name of scenario to run (if file contains multiple)')

# Simulation options
simOpts = parser.add_argument_group('dynamic simulation options')
simOpts.add_argument('--time', help='time bound for simulations (default none)',
                     type=int, default=None)
simOpts.add_argument('--count', help='number of successful simulations to run (default infinity)',
                     type=int, default=0)
simOpts.add_argument('--max-sims-per-scene', type=int, default=1, metavar='N',
                     help='max # of rejected simulations before sampling a new scene (default 1)')
# simOpts.add_argument('--image-limit', help='max number of images to generate (default none)',
#                      type=int, default=None)

# Interactive rendering options
intOptions = parser.add_argument_group('static scene diagramming options')
intOptions.add_argument('-d', '--delay', type=float,
                        help='loop automatically with this delay (in seconds) '
                             'instead of waiting for the user to close the diagram')
intOptions.add_argument('-z', '--zoom', help='zoom expansion factor (default 1)',
                        type=float, default=1)

# Debugging options
debugOpts = parser.add_argument_group('debugging options')
debugOpts.add_argument('--show-params', help='show values of global parameters',
                       action='store_true')
debugOpts.add_argument('--show-records', help='show values of recorded expressions',
                       action='store_true')
debugOpts.add_argument('-b', '--full-backtrace', help='show full internal backtraces',
                       action='store_true')
debugOpts.add_argument('--pdb', action='store_true',
                       help='enter interactive debugger on errors (implies "-b")')
ver = metadata.version('scenic')
debugOpts.add_argument('--version', action='version', version=f'Scenic {ver}',
                       help='print Scenic version information and exit')
debugOpts.add_argument('--dump-initial-python', help='dump initial translated Python',
                       action='store_true')
debugOpts.add_argument('--dump-ast', help='dump final AST', action='store_true')
debugOpts.add_argument('--dump-python', help='dump Python equivalent of final AST',
                       action='store_true')
debugOpts.add_argument('--no-pruning', help='disable pruning', action='store_true')
debugOpts.add_argument('--gather-stats', type=int, metavar='N',
                       help='collect timing statistics over this many scenes')

parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                    help=argparse.SUPPRESS)

# Positional arguments
parser.add_argument('scenicFile', help='a Scenic file to run', metavar='FILE')

# Parse arguments and set up configuration
args = parser.parse_args()
delay = args.delay
errors.showInternalBacktrace = args.full_backtrace
if args.pdb:
    errors.postMortemDebugging = True
    errors.showInternalBacktrace = True
params = {}
for name, value in args.param:
    # Convert params to ints or floats if possible
    try:
        value = int(value)
    except ValueError:
        try:
            value = float(value)
        except ValueError:
            pass
    params[name] = value
translator.dumpTranslatedPython = args.dump_initial_python
translator.dumpFinalAST = args.dump_ast
translator.dumpASTPython = args.dump_python
translator.verbosity = args.verbosity
translator.usePruning = not args.no_pruning
if args.seed is not None and args.verbosity >= 1:
    print(f'Using random seed = {args.seed}')
    random.seed(args.seed)

# Load scenario from file
if args.verbosity >= 1:
    print('Beginning scenario construction...')
startTime = time.time()
scenario = errors.callBeginningScenicTrace(
    lambda: translator.scenarioFromFile(args.scenicFile,
                                        params=params,
                                        model=args.model,
                                        scenario=args.scenario)
)
totalTime = time.time() - startTime
if args.verbosity >= 1:
    print(f'Scenario constructed in {totalTime:.2f} seconds.')

if args.simulate:
    simulator = errors.callBeginningScenicTrace(scenario.getSimulator)

def generateScene():
    # startTime = time.time()
    scenes, stats = errors.callBeginningScenicTrace(
        lambda: scenario.generate(verbosity=args.verbosity)
    )
    if args.verbosity >= 1:
        # totalTime = time.time() - startTime
        i = stats['num_iterations']
        t = stats['time']
        if stats['success']:
            print(f'  Generated {len(scenes)} scene(s) in {i} iterations, {t:.4g} seconds.')
        else:
            print(f'  Failed to generated a scene in {i-1} iterations, {t:.4g} seconds.')
        if args.show_params:
            for param, value in scene.params.items():
                print(f'    Parameter "{param}": {value}')
    return scenes, stats

def runSimulation(scene):
    startTime = time.time()
    if args.verbosity >= 1:
        print(f'  Beginning simulation of {scene.dynamicScenario}...')
    try:
        simulation = errors.callBeginningScenicTrace(
            lambda: simulator.simulate(scene, maxSteps=args.time, verbosity=args.verbosity,
                                       maxIterations=args.max_sims_per_scene)
        )
    except SimulationCreationError as e:
        if args.verbosity >= 1:
            print(f'  Failed to create simulation: {e}')
        return False, None
    if args.verbosity >= 1:
        totalTime = time.time() - startTime
        print(f'  Ran simulation in {totalTime:.4g} seconds.')
    if simulation and args.show_records:
        for name, value in simulation.result.records.items():
            if isinstance(value, list):
                print(f'    Record "{name}": (time series)')
                for step, subval in value:
                    print(f'      {step:4d}: {subval}')
            else:
                print(f'    Record "{name}": {value}')
    return simulation is not None, simulation.stats

try:
    if args.gather_stats is None:   # Generate scenes interactively until killed
        import matplotlib.pyplot as plt
        successCount = 0
        # print(args.count)
        # print(successCount)
        # print(successCount <= args.count)
        ws = params.get('outputWS')
        save_imgs = params.get('saveImgs') == 'True'
        save_files = params.get('saveFiles') == 'True'
        save_paths = params.get('savePaths') == 'True'
        view_paths = params.get('showPaths') == 'True'
        view_imgs = params.get('viewImgs') == 'True'
        get_meas_stats = params.get('saveStats') == 'True'
        save_sim_stats = params.get('sim-saveStats') == 'True'

        save_something = save_imgs or save_files or get_meas_stats or save_sim_stats or save_paths
        get_abs_scene = params.get('getAbsScene')
        if get_abs_scene not in ['all', 'scenic', 'evol', 'dyn', None]:
            exit('Invalid specification for <getAbsScene> parameter')
        assert ws or not save_something, 'You need to specify the outputWS parameter if you want to save stuff.'
        assert not view_paths or view_imgs

        # Define save folder path
        folderName = params.get('outputDir')
        if folderName == None or folderName == "None":
            folderName = datetime.now().strftime("%m-%d-%H-%M-%S")
        p = f'{ws}/{folderName}'
        if save_something:
            Path(f'{p}/').mkdir(parents=True, exist_ok=True)

        meas_path = f'{p}/_measurementstats.json'
        json_path = f'{p}/_genstats.json'
        
        if get_meas_stats:
            measurementStats = {}
            measurementStats['map'] = scenario.params.get('map')
            measurementStats['num_actors'] = len(scenario.objects)
            measurementStats['sourcePath'] = args.scenicFile
            approach = 'unspecified'
            b_name = os.path.basename(args.scenicFile)
            if b_name.startswith('d-') :
                approach = b_name[2:-7]
            measurementStats['approach'] = approach
            measurementStats['results'] = []


        # Static Analysis
        if params.get('static-element-at') != None:
            # TODO this is very temporary
            pt = json.loads(params.get('static-element-at'))
            elem = scenario.network.elementAt(pt)
            print(elem)
            exit()
        if params.get('static-analysis') == 'True':
            doStaticAnalysis(scenario, p)
            exit()

        # Scenario generation
        absSceneStatsMap = {}
        count = args.count
        # LEGACY
        # if params.get('evol-NumSols') == 'measurement' and get_meas_stats :
        #     count *= 2
        while (count == 0 or successCount < count):

            # #############################
            # We implement a 2-STEP PROCESS
            # ############################# 

            #########
            # STEP 1:
            # From an abstract scene spec given as input,
            # Generate 1+ initial scene, where all inital concrete positions are defined
            scenes, stats = generateScene()
            prevSuccessCount = successCount
            if get_meas_stats:
                measurementStats['results'].append(stats)
                print(f'  Saved measurement stats at    {meas_path}')
                with open(meas_path, 'w') as outfile:
                    json.dump(measurementStats, outfile, indent=4)

            for i, scene in enumerate(scenes):
                dirPath = f'{p}/{prevSuccessCount}-{i}'
                if save_files or save_imgs:
                    os.makedirs(dirPath, exist_ok=True)
                if scene is None:
                    # failed to generate scene
                    successCount +=1
                    # currently, the count is the number of attempts
                    continue
                # SAVE
                printer.printToFile(scene, save_files, get_abs_scene, path=dirPath, jsonpath=json_path, jsonstats=absSceneStatsMap)

                # MATPLOTLIB representation
                if save_imgs or view_imgs or save_paths:
                    image_params = {'save_im':save_imgs, 'view_im':view_imgs, 'view_path':view_paths}
                    if delay is None:
                        scene.show(zoom=args.zoom, dirPath=dirPath, params=image_params)
                    else:
                        scene.show(zoom=args.zoom, dirPath=dirPath, params=image_params, block=False)
                        plt.pause(delay)
                        plt.clf()
                    # successCount += 1

                # SIMULATION
                if args.simulate:
                
                    #########
                    # STEP 2:
                    # For each generated concrete initial scene,
                    # Add dynamic components (speeds and behaviors)
                    n_dyn_abstract_scenes = 1 if params.get('sim-extend') == 'False' else params.get('sim-n-absScenes')
                    n_dyn_conctretizations = 1 if 'sim-n-concretizations' not in params else params.get('sim-n-concretizations')
                    n_dyn_simulations = 1 if 'sim-n-sims' not in params else params.get('sim-n-sims')
                    
                    # >>> ABSTRACT SCENE
                    for abs_scene_id in range(n_dyn_abstract_scenes):

                        dyn_abs_cons = dyn_util.gatherAbsCons(scene)
                        all_res = []

                        # >>> CONCRETE SCENE
                        for k in range(n_dyn_conctretizations):

                            conc_speeds = dyn_util.concretizeDynamicAbstractScene(scene, dyn_abs_cons, scenario.network)
                            if not conc_speeds:
                                continue
                                                                                  
                            dyn_conc_res = dyn_util.init_agg_res(conc_speeds) # FOR AGGREGATION
                            
                            for j in range(n_dyn_simulations):

                                success, sim_stats = runSimulation(scene)
                                # if success:
                                #     successCount += 1
                                if save_sim_stats:
                                    sim_stats_path = f'{dirPath}/abstractscene{abs_scene_id}/concretization{k}/_rep{j}Stats.json'
                                    dyn_util.save_particular_file(sim_stats_path, sim_stats)

                                    dyn_util.update_agg_res(dyn_conc_res, success, sim_stats) # FOR AGGREGATION
                                    
                            if save_sim_stats:
                                all_res.append(dyn_conc_res)
                                path_agg = f'{dirPath}/abstractscene{abs_scene_id}/_simstats.json'
                                dyn_util.save_aggregate_file(path_agg, scenario, args.scenicFile, dyn_abs_cons, all_res)

                successCount += 1
            gc.collect()
            gc.collect()
            gc.collect()
    else:   # Gather statistics over the specified number of scenes
        its = []
        startTime = time.time()
        while len(its) < args.gather_stats:
            scene, iterations = generateScene()
            its.append(iterations)
        totalTime = time.time() - startTime
        count = len(its)
        print(f'Sampled {len(its)} scenes in {totalTime:.2f} seconds.')
        print(f'Average iterations/scene: {sum(its)/count}')
        print(f'Average time/scene: {totalTime/count:.2f} seconds.')

except KeyboardInterrupt:
    pass

finally:
    if args.simulate:
        simulator.destroy()

def dummy():    # for the 'scenic' entry point to call after importing this module
    pass

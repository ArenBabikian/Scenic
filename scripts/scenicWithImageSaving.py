
### Top-level functionality of the scenic package as a script:
### load a scenario and generate scenes in an infinite loop.

import sys
import time
import argparse
import random
# import importlib.metadata
import weakref
import carla
from carla import ColorConverter as cc
from collections import OrderedDict

try:
    import numpy as np
except ImportError:
    raise RuntimeError('cannot import numpy, make sure numpy package is installed')

from scenic.core.object_types import disableDynamicProxyFor

import scenic.syntax.translator as translator
from scenic.core.distributions import RejectionException
import scenic.core.dynamics as dynamics
import scenic.core.errors as errors
from scenic.core.simulators import SimulationCreationError, RejectSimulationException, EndSimulationAction, SimulationResult

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
simOpts.add_argument('--res', help='window resolution (default: 1280x720)', default='480x320',
                     metavar='WIDTHxHEIGHT')
simOpts.add_argument('-o', '--output',
                     help='path to derictory where images will be saved (default: output)')
simOpts.add_argument('--gamma', default=2.2, type=float,
                     help='Gamma correction of the camera (default: 2.2)')
simOpts.add_argument('--timestep', type=float, default=0.1, 
                     help='simulation time (seconds) that goes by between steps, should not exceed 0.1 (default 0.1)')
simOpts.add_argument('--samplingrate', type=int, default=1, 
                     help='the images will be saved every n-th step (default 1)')

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
debugOpts.add_argument('-b', '--full-backtrace', help='show full internal backtraces',
                       action='store_true')
debugOpts.add_argument('--pdb', action='store_true',
                       help='enter interactive debugger on errors (implies "-b")')
# ver = importlib.metadata.version('scenic')
ver = '0.9.13'
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
args.width, args.height = [int(x) for x in args.res.split('x')]
timestep = args.timestep
samplingrate = args.samplingrate
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
params['no-validation']='True'
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
    settings = simulator.world.get_settings()
    settings.fixed_delta_seconds = timestep
    simulator.world.apply_settings(settings)


class CameraManager(object):
    def __init__(self, parent_actor, width, hight, gamma_correction, location_index, output_dir=None):
        self.sensor = None
        self._parent = parent_actor
        self.images = []
        self.output_dir = output_dir
        self.recording = output_dir is not None
        bound_y = 0.5 + self._parent.bounding_box.extent.y
        Attachment = carla.AttachmentType
        self._camera_transforms = [
            (carla.Transform(carla.Location(x=-5.5, z=2.5), carla.Rotation(pitch=8.0)), Attachment.SpringArm),
            (carla.Transform(carla.Location(x=1.6, z=1.7)), Attachment.Rigid),
            (carla.Transform(carla.Location(x=5.5, y=1.5, z=1.5)), Attachment.SpringArm),
            (carla.Transform(carla.Location(x=-8.0, z=6.0), carla.Rotation(pitch=6.0)), Attachment.SpringArm),
            (carla.Transform(carla.Location(x=-1, y=-bound_y, z=0.5)), Attachment.Rigid),
            (carla.Transform(carla.Location(x=0, z=1.7)), Attachment.Rigid)]
        self.transform_index = location_index
        self.sensors = [
            ['sensor.camera.rgb', cc.Raw, 'Camera RGB', {}],
            ['sensor.camera.instance_segmentation', cc.Raw, 'raw', {}],
            ['sensor.camera.depth', cc.Raw, 'Camera Depth (Raw)', {}],
            ['sensor.camera.depth', cc.Depth, 'Camera Depth (Gray Scale)', {}],
            ['sensor.camera.depth', cc.LogarithmicDepth, 'Camera Depth (Logarithmic Gray Scale)', {}],
            ['sensor.camera.semantic_segmentation', cc.Raw, 'Camera Semantic Segmentation (Raw)', {}],
            ['sensor.camera.semantic_segmentation', cc.CityScapesPalette,
                'Camera Semantic Segmentation (CityScapes Palette)', {}],
            ['sensor.lidar.ray_cast', None, 'Lidar (Ray-Cast)', {'range': '50'}],
            ['sensor.camera.dvs', cc.Raw, 'Dynamic Vision Sensor', {}],
            ['sensor.camera.rgb', cc.Raw, 'Camera RGB Distorted',
                {'lens_circle_multiplier': '3.0',
                'lens_circle_falloff': '3.0',
                'chromatic_aberration_intensity': '0.5',
                'chromatic_aberration_offset': '0'}]]
        world = self._parent.get_world()
        bp_library = world.get_blueprint_library()
        for item in self.sensors:
            bp = bp_library.find(item[0])
            if item[0].startswith('sensor.camera'):
                bp.set_attribute('image_size_x', str(width))
                bp.set_attribute('image_size_y', str(hight))
                if bp.has_attribute('gamma'):
                    bp.set_attribute('gamma', str(gamma_correction))
                for attr_name, attr_value in item[3].items():
                    bp.set_attribute(attr_name, attr_value)
            elif item[0].startswith('sensor.lidar'):
                self.lidar_range = 50

                for attr_name, attr_value in item[3].items():
                    bp.set_attribute(attr_name, attr_value)
                    if attr_name == 'range':
                        self.lidar_range = float(attr_value)

            item.append(bp)
        self.index = None

    def set_sensor(self, index, ):
        index = index % len(self.sensors)
        needs_respawn = True if self.index is None \
            else self.sensors[index][2] != self.sensors[self.index][2]
        if needs_respawn:
            if self.sensor is not None:
                self.sensor.destroy()
                self.surface = None
            self.sensor = self._parent.get_world().spawn_actor(
                self.sensors[index][-1],
                self._camera_transforms[self.transform_index][0],
                attach_to=self._parent,
                attachment_type=self._camera_transforms[self.transform_index][1])
            # We need to pass the lambda a weak reference to self to avoid
            # circular reference.
            weak_self = weakref.ref(self)
            self.sensor.listen(lambda image: CameraManager._parse_image(weak_self, image))
        self.index = index

    def toggle_recording(self):
        self.recording = not self.recording

    def _parse_image(weak_self, image):
        self = weak_self()
        if not self:
            return
        else:
            image.convert(self.sensors[self.index][1])
            # array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
            # array = np.reshape(array, (image.height, image.width, 4))
            # array = array[:, :, :3]
            # array = array[:, :, ::-1]
            # self.surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
        if self.recording:
            # print(image.frame)
            # print(samplingrate)
            # print(image.frame % samplingrate)
            if image.frame % samplingrate == 0:
                # print('ADDED')
                self.images.append(image)

    def destroy_sensor(self):
        if self.sensor is not None:
            self.sensor.stop()
            self.sensor.destroy()


def generateScene():
    startTime = time.time()
    scene, iterations = errors.callBeginningScenicTrace(
        lambda: scenario.generate(verbosity=args.verbosity, maxIterations=10000)
    )
    if args.verbosity >= 1:
        totalTime = time.time() - startTime
        print(f'  Generated scene in {iterations} iterations, {totalTime:.4g} seconds.')
        if args.show_params:
            for param, value in scene.params.items():
                print(f'    Parameter "{param}": {value}')
    return scene, iterations

def run(simulation, maxSteps):
    """Run the simulation.

    Throws a RejectSimulationException if a requirement is violated.
    """
    trajectory = simulation.trajectory
    if simulation.currentTime > 0:
        raise RuntimeError('tried to run a Simulation which has already run')
    assert len(trajectory) == 1
    actionSequence = []

    import scenic.syntax.veneer as veneer
    veneer.beginSimulation(simulation)
    dynamicScenario = simulation.scene.dynamicScenario

    try:
        # Initialize dynamic scenario
        dynamicScenario._start()

        # Update all objects in case the simulator has adjusted any dynamic
        # properties during setup
        simulation.updateObjects()

        # Run simulation
        assert simulation.currentTime == 0
        terminationReason = None
        while maxSteps is None or simulation.currentTime < maxSteps:
            if simulation.verbosity >= 3:
                print(f'    Time step {simulation.currentTime}:')

            # Run compose blocks of compositional scenarios
            terminationReason = dynamicScenario._step()

            # Check if any requirements fail
            dynamicScenario._checkAlwaysRequirements()

            # Run monitors
            newReason = dynamicScenario._runMonitors()
            if newReason is not None:
                terminationReason = newReason

            # "Always" and scenario-level requirements have been checked;
            # now safe to terminate if the top-level scenario has finished
            # or a monitor requested termination
            if terminationReason is not None:
                break
            terminationReason = dynamicScenario._checkSimulationTerminationConditions()
            if terminationReason is not None:
                break

            # Compute the actions of the agents in this time step
            allActions = OrderedDict()
            schedule = simulation.scheduleForAgents()
            for agent in schedule:
                behavior = agent.behavior
                if not behavior._runningIterator:   # TODO remove hack
                    behavior.start(agent)
                actions = behavior.step()
                if isinstance(actions, EndSimulationAction):
                    terminationReason = str(actions)
                    break
                assert isinstance(actions, tuple)
                if len(actions) == 1 and isinstance(actions[0], (list, tuple)):
                    actions = tuple(actions[0])
                if not simulation.actionsAreCompatible(agent, actions):
                    raise errors.InvalidScenarioError(f'agent {agent} tried incompatible '
                                                f' action(s) {actions}')
                allActions[agent] = actions
            if terminationReason is not None:
                break

            # Execute the actions
            if simulation.verbosity >= 3:
                for agent, actions in allActions.items():
                    print(f'      Agent {agent} takes action(s) {actions}')
            simulation.executeActions(allActions)

            # Run the simulation for a single step and read its state back into Scenic
            simulation.step()
            simulation.updateObjects()
            simulation.currentTime += 1

            # Save the new state
            trajectory.append(simulation.currentState())
            actionSequence.append(allActions)

        if terminationReason is None:
            terminationReason = f'reached time limit ({maxSteps} steps)'
        return True
        result = SimulationResult(trajectory, actionSequence, terminationReason)
        return result
    finally:
        simulation.destroy()
        for obj in simulation.scene.objects:
            disableDynamicProxyFor(obj)
        for agent in simulation.agents:
            agent.behavior.stop()
        for monitor in simulation.scene.monitors:
            monitor.stop()
        veneer.endSimulation(simulation)

def simulate(scene, maxSteps=None, maxIterations=100, verbosity=0,
                raiseGuardViolations=False):
    """Run a simulation for a given scene."""

    # Repeatedly run simulations until we find one satisfying the requirements
    iterations = 0
    while maxIterations is None or iterations < maxIterations:
        iterations += 1
        # Run a single simulation
        try:
            simulation = simulator.createSimulation(scene, verbosity=verbosity)
            all_cameras = []
            # i = 5
            # c =CameraManager(simulation.ego.carlaActor, args.width, args.height, 2.2, i, f'{args.output}/{i}cam/')
            # c.set_sensor(0)
            # all_cameras.append(c)
            for i in range(6):
                c =CameraManager(simulation.ego.carlaActor, args.width, args.height, 2.2, i, f'{args.output}/{i}cam/')
                c.set_sensor(0)
                all_cameras.append(c)
            # semsegCamera = CameraManager(simulation.ego.carlaActor, args.width, args.height, 2.2, 5, '%s/semseg/' % args.output)
            # semsegCamera.set_sensor(6)
            # semsegCamera = CameraManager(simulation.ego.carlaActor, args.width, args.height, 2.2, '%s/semseg/' % args.output)
            # semsegCamera.set_sensor(1)
            result = run(simulation, maxSteps)
            for i, cam in enumerate(all_cameras):
                for image in cam.images:
                    save_path = f'{args.output}/{i}cam/{image.frame:06d}'
                    image.save_to_disk(save_path)
                    print(f'image saved to {save_path}')
            #     cam.destroy_sensor()
        except (RejectSimulationException, RejectionException, dynamics.GuardViolation) as e:
            if verbosity >= 2:
                print(f'  Rejected simulation {iterations} at time step '
                        f'{simulation.currentTime} because of: {e}')
            if raiseGuardViolations and isinstance(e, dynamics.GuardViolation):
                raise
            else:
                continue
        # Completed the simulation without violating a requirement
        if verbosity >= 2:
            print(f'  Simulation {iterations} ended successfully at time step '
                    f'{simulation.currentTime} because of: {result.terminationReason}')
        return result
    return None

def runSimulation(scene):
    scene=scene[0]
    startTime = time.time()
    if args.verbosity >= 1:
        print(f'  Beginning simulation of {scene.dynamicScenario}...')
    try:
        result = errors.callBeginningScenicTrace(
            lambda: simulate(scene, maxSteps=args.time, verbosity=args.verbosity,
                                       maxIterations=args.max_sims_per_scene)
        )
    except SimulationCreationError as e:
        if args.verbosity >= 1:
            print(f'  Failed to create simulation: {e}')
        return False
    if args.verbosity >= 1:
        totalTime = time.time() - startTime
        print(f'  Ran simulation in {totalTime:.4g} seconds.')
    return result is not None

try:
    if args.gather_stats is None:   # Generate scenes interactively until killed
        import matplotlib.pyplot as plt
        successCount = 0
        while True:
            scene, _ = generateScene()
            if args.simulate:
                success = runSimulation(scene)
                if success:
                    successCount += 1
                    if 0 < args.count <= successCount:
                        break
            else:
                if delay is None:
                    scene.show(zoom=args.zoom)
                else:
                    scene.show(zoom=args.zoom, block=False)
                    plt.pause(delay)
                    plt.clf()
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

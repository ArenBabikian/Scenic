
import math

from matplotlib.colors import to_rgb
from scenic.core.map.map_visualisation_utils import showPairwiseCollidingRegions, zoomToIntersection
from scenic.core.vectors import Vector
from scenic.core.visuals.utils import clean_fig, show_network_alt
from scenic.simulators.carla.utils.utils import scenicToCarlaLocation


def figs_src(scene, dirPath=None, view=False):
    """Render a schematic of the scene for debugging."""
    
    import matplotlib.pyplot as plt
    # SETUP
    green = '#009900'
    blue = '#0066CC'
    red = '#990000'

    r1 = scene.workspace.network.elements['road93_lane0']
    r2 = scene.workspace.network.elements['road102_lane0']

    # ###############
    # FIG 1 : lane regions
    clean_fig(plt)
    # scene.workspace.show(plt)
    show_network_alt(scene.workspace.network, plt)

    def show_reg(r, c):
        r.show(plt, style='-', color=c)
        points = tuple(r.polygons[0].exterior.coords)
        x, y = zip(*points)
        plt.fill(x, y, color=c)

    # Add regions
    show_reg(r1, blue)
    show_reg(r2, green)
    showPairwiseCollidingRegions([r1, r2], plt, red)
    zoomToIntersection(scene, plt, 3)

    # save and view
    filePath = f'{dirPath}/fig1.png'
    plt.savefig(filePath)
    print(f'  Saved image at                {filePath}')
    plt.show() if view else None
    plt.clf()

    # ###############
    # FIG 2 : exact paths
    clean_fig(plt)
    show_network_alt(scene.workspace.network, plt)

    def show_cl(cl, c):
        # Centerlines
        cl.show(plt, style='--', color=c, linewidth=5)

        # Arrows
        assert cl.length >= 10
        pts = cl.equallySpacedPoints(0.2, normalized=True)
        pts.append(cl[-1])
        pts.pop(0)

        hs = [cl.orientation[pt] for pt in pts]
        x, y = zip(*pts)
        u = [math.cos(h + (math.pi/2)) for h in hs]
        v = [math.sin(h + (math.pi/2)) for h in hs]
        ql = 10
        # scale=0.06 is half as small as scale=0.03
        plt.quiver(x, y, u, v,
                   headlength=ql, headaxislength=ql,
                   headwidth=2*ql/3,
                   scale=0.03, units='dots',
                   pivot='middle', color=c)

    show_cl(r1.centerline, blue)
    show_cl(r2.centerline, green)
    # Add collision point
    plt.plot(88.88, -326.58, 'o', markersize=20, color=red, markeredgecolor='white', markeredgewidth=2)
    
    zoomToIntersection(scene, plt, 3)

    # save and view
    filePath = f'{dirPath}/fig2.png'
    plt.savefig(filePath)
    print(f'  Saved image at                {filePath}')
    plt.show() if view else None
    plt.clf()

    # ###############
    # FIG 3 : CARLA integration

    # Run CARLA
    import carla
    client = carla.Client("172.30.208.1", 2000)
    client.set_timeout(5.0)
    world = client.get_world()

    if world.get_map().name != "Town01":
        client.load_world("Town01")
    world.set_weather(getattr(carla.WeatherParameters, 'Default'))
    # 'Default', 'ClearNoon', 'CloudyNoon', 'WetNoon', 'WetCloudyNoon', 'MidRainyNoon',
    # 'HardRainNoon', 'SoftRainNoon', 'ClearSunset', 'CloudySunset', 'WetSunset',
    # 'WetCloudySunset', 'MidRainSunset', 'HardRainSunset', 'SoftRainSunset'

    def spawn_vehicle(world, color, loc_vehicle):
        # NOTE: color must be a string of the form "R,G,B"

        bp_vehicle = world.get_blueprint_library().find("vehicle.bmw.grandtourer")
        bp_vehicle.set_attribute('color', color)
        tr_vehicle = world.get_map().get_waypoint(loc_vehicle).transform
        tr_vehicle.location = tr_vehicle.location + carla.Location(0,0,5)
        world.spawn_actor(bp_vehicle, tr_vehicle)

    # spawn vehicles
    def to_rgb_256(color):
        return ','.join(str(int(x*256)) for x in to_rgb(color))

    spawn_vehicle(world, to_rgb_256(green), scenicToCarlaLocation(Vector(86.26, -328.67), world=world))
    spawn_vehicle(world, to_rgb_256(blue), scenicToCarlaLocation(Vector(93.77,-326.63), world=world))

    # Spawn camera
    loc = carla.Location(x=90.116943, y=326.180023, z=15.212180)
    rot = carla.Rotation(pitch=-88.996330, yaw=90.116592, roll=-179.989273)
    world.get_spectator().set_transform(carla.Transform(loc, rot))

    # save image
    # TODO missing scenic integration with the simulatorand the cameraManager
    # This would allow for automatic image saving
        
    input("press ENTER to finish.")

    for actor in world.get_actors().filter('vehicle.*'):
        actor.destroy()
    print('Actors Destroyed.')



import math
from scenic.core.geometry import averageVectors

from scenic.core.object_types import Object
from scenic.core.regions import RectangularRegion

def clean_fig(plt):
    plt.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False, labelbottom=False, labelleft=False)
    plt.box(False)
    plt.margins(0, 0)
    plt.tight_layout(pad=0)
    plt.gca().set_aspect('equal')


def show_network_alt(network, plt):
        colors = {'walk' : '#00A0FF',
                  'shoulder' : '#606060',
                  'road' : '#FF0000',
                  'intersection' : '#00FF00',
                  'cl' : '#A0A0A0'}
        grey = '#808080'
        # network.walkableRegion.show(plt, style='-', color='#00A0FF')
        # network.shoulderRegion.show(plt, style='-', color='#606060')
        network.shoulderRegion.show(plt, style='-', color=grey)
        for road in network.roads:
            road.show(plt, style='-', color=grey)
            for lane in road.lanes:     # will loop only over lanes of main roads
                lane.leftEdge.show(plt, style='--', color=grey)
                lane.rightEdge.show(plt, style='--', color=grey)

                # # Draw arrows indicating road direction
                # if lane.centerline.length >= 10:
                #     pts = lane.centerline.equallySpacedPoints(5)
                # else:
                #     pts = [lane.centerline.pointAlongBy(0.5, normalized=True)]
                # hs = [lane.centerline.orientation[pt] for pt in pts]
                # x, y = zip(*pts)
                # u = [math.cos(h + (math.pi/2)) for h in hs]
                # v = [math.sin(h + (math.pi/2)) for h in hs]
                # plt.quiver(x, y, u, v,
                #            pivot='middle', headlength=4.5,
                #            scale=0.06, units='dots', color='#A0A0A0')
        # for lane in network.lanes:     # draw centerlines of all lanes (including connecting)
        #     lane.centerline.show(plt, style=':', color='#A0A0A0')

        # network.intersectionRegion.show(plt, style='g')
        network.intersectionRegion.show(plt, style=grey)


def show_regions(plt, regions, c):
    for r in regions:
        show_reg(plt, r, c)

def show_reg(plt, r, c):
    r.show(plt, style='-', color=c)
    points = tuple(r.polygons[0].exterior.coords)
    x, y = zip(*points)
    plt.fill(x, y, color=c)


def show_cl(plt, cl, c):
    cl.show(plt, style='--', color=c, linewidth=5)


def show_arrows(plt, cl, c, pointsDelts=-1, rmFirst=False, size=1, zorder=100):

    # Positions
    if pointsDelts == -1:
        assert cl.length >= 10
        pts = cl.equallySpacedPoints(0.2, normalized=True)
    else:
        pts = cl.equallySpacedPoints(pointsDelts)

    # Corner cases
    if rmFirst:
        pts.append(cl[-1])
        pts.pop(0)

    # Drawing
    hs = [cl.orientation[pt] for pt in pts]
    x, y = zip(*pts)
    u = [math.cos(h + (math.pi/2)) for h in hs]
    v = [math.sin(h + (math.pi/2)) for h in hs]
    ql = 10
    # scale=0.06 is half as big as scale=0.03
    scale = 0.03/size
    plt.quiver(x, y, u, v,
                headlength=ql, headaxislength=ql,
                headwidth=2*ql/3,
                scale=scale, units='dots',
                pivot='middle', color=c,
                zorder=zorder)


def show_object(plt, pos, head, c, size=(3, 5), zorder=101):
    objectregion = RectangularRegion(pos, head, size[0], size[1])
    corners = objectregion.corners
    x, y = zip(*corners)
    plt.fill(x, y, color=c, zorder=zorder)

    frontMid = averageVectors(corners[0], corners[1])
    baseTriangle = [frontMid, corners[2], corners[3]]
    triangle = [averageVectors(p, pos, weight=0.5) for p in baseTriangle]
    x, y = zip(*triangle)
    plt.fill(x, y, "w", zorder=zorder)
    plt.plot(x + (x[0],), y + (y[0],), color="k", linewidth=1, zorder=zorder)

def show_carla_intersection(actors_list, camera=None, weather='Default'):

    from scenic.simulators.carla.utils.utils import scenicToCarlaLocation
    from matplotlib.colors import to_rgb
    from scenic.core.type_support import toVector
    
    import carla
    client = carla.Client("172.30.208.1", 2000)
    client.set_timeout(5.0)
    world = client.get_world()

    if world.get_map().name != "Town01":
        client.load_world("Town01")
    world.set_weather(getattr(carla.WeatherParameters, weather))
    # 'Default', 'ClearNoon', 'CloudyNoon', 'WetNoon', 'WetCloudyNoon', 'MidRainyNoon',
    # 'HardRainNoon', 'SoftRainNoon', 'ClearSunset', 'CloudySunset', 'WetSunset',
    # 'WetCloudySunset', 'MidRainSunset', 'HardRainSunset', 'SoftRainSunset'

    for actor_specs in actors_list:
        pos = actor_specs['position']
        carla_location = scenicToCarlaLocation(toVector(pos), world=world)

        color = actor_specs['color'] if 'color' in actor_specs else '#000000'
        str_color = ','.join(str(int(x*256)) for x in to_rgb(color))

        model = actor_specs['model'] if 'model' in actor_specs else "vehicle.bmw.grandtourer"

        bp_vehicle = world.get_blueprint_library().find(model)
        bp_vehicle.set_attribute('color', str_color) # NOTE: color must be a string of the form "R,G,B"
        tr_vehicle = world.get_map().get_waypoint(carla_location).transform
        tr_vehicle.location = tr_vehicle.location + carla.Location(0,0,5)
        world.spawn_actor(bp_vehicle, tr_vehicle)

    # Spawn camera
    if camera is None:
        camera = {
            'x':90.116943, 'y':326.180023, 'z':15.212180,
            'pitch':-88.996330, 'yaw':90.116592, 'roll':-179.989273
        }
    loc = carla.Location(camera['x'], camera['y'], camera['z'])
    rot = carla.Rotation(camera['pitch'], camera['yaw'], camera['roll'])
    world.get_spectator().set_transform(carla.Transform(loc, rot))

    # save image
    # TODO missing scenic integration with the simulatorand the cameraManager
    # This would allow for automatic image saving
        
    input("press ENTER to finish.")

    for actor in world.get_actors().filter('vehicle.*'):
        actor.destroy()
    print('Actors Destroyed.')


def save_show_clear(plt, filePath, view):
    clean_fig(plt)

    plt.savefig(filePath)
    print(f'  Saved image at                {filePath}')
    plt.show() if view else None
    plt.clf()
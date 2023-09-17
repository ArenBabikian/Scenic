
import math
import os
import scenic.core.printer.utils as util
from scenic.simulators.carla.utils.utils import scenicToCarlaLocation, scenicToCarlaRotation
from scenic.simulators.utils.colors import Color
from pathlib import Path

FILE2TOWNNAME = {'town05':'Town05',
                 'town07':'Town07',
                 'tram05-mod':'Krisztina'}
EGO_DIST_BEFORE_JUNC = 5
SECONDS_GIVEN_PER_METERS = 0.8
INITIAL_SECONDS_DELAY = 5.0

#########################
# EXACT SCENE

def saveExactCoords(scene, path=None):
    filePath = f'{path}/exactCoords.scenic'
    ego = scene.egoObject
    with open(filePath, "w") as f:
        f.write(util.getParamMap(scene))
        f.write('model scenic.simulators.carla.model\n')
        f.write('\n')
        # Actor initializations
        for i in range(len(scene.objects)):
            o = scene.objects[i]
            oName = f'o{i}'
            if o is ego:
                oName = 'ego'
            col = o.color
            if type(col) is Color:
                col = [col.r, col.g, col.b]
            f.write(f'{oName} = Car at {o.position}, with color{o.color}\n')
    print(f'  Saved exact coordinates at    {filePath}')


#########################
# DYNAMIC SCENE

def findPointInLane(lane):

    cl = lane.centerline

    start = cl.points[0]
    # mid = cl.points[int(len(cl.points)/2)] # causing problems for straight roads (2 points) and for roads if they have inconsistent distances between points
    end = cl.points[-1]
    return start, end


def savePathXml(scene, trajectories, path, longPaths=False):
    filePath = f'{path}/paths.xml'

    if longPaths:
        exit('Long paths not handled currently')
    else:
        with open(filePath, "w") as f:
            for a in trajectories:
                _, s = findPointInLane(trajectories[a][0])

                sh = (scene.workspace.network._defaultRoadDirection(s)) * 180 / math.pi
                # _, m, _ = findPointInLane(trajectories[a][1])
                c = a.position
                _, e = findPointInLane(trajectories[a][2])
                f.write(f'{str(a)} >>> start{s}{sh}, current{c}, end{e}\n')

def savePathXml(scene, filePath):


    content = getScenarioDesc(scene)
    with open(filePath, "w") as f:
        f.writelines(content)
    print(f'  Saved path xml file at        {filePath}')


def getScenarioDesc(scene):
    '''
    <?xml version='1.0' encoding='UTF-8'?>
    <routes>
        <route id="0" town="Town05" intersection_id="1574" timeout="20">
                <waypoint x="-50.85" y="65.75" z="0.0" maneuver='left'/>
                <other_actor x="-10.33" y="88.02" z="0.0" yaw="180" speed="15" maneuver='left' model="vehicle.tesla.model3"/>
                <other_actor x="-68.11" y="94.96" z="0.0" yaw="0" speed="20" maneuver='right' model="vehicle.tesla.model3"/>
                <weather id="ClearSunset" cloudiness="20.000000" precipitation="0.000000" precipitation_deposits="50.000000" wind_intensity="0.350000" sun_azimuth_angle="90.000000" sun_altitude_angle="75.000000" fog_density="0.000000" fog_distance="0.000000" fog_falloff="0.000000" wetness="0.000000"/>
        </route>
    </routes>
    '''
    # SETUP
    route_id = 0 #TODO

    map_name = Path(scene.params.get('map')).stem
    town = FILE2TOWNNAME[map_name]

    intersection_id = scene.params.get('intersectiontesting')

    # Compute Timeout
    dist_in_junc = scene.objects[0].currentLane.centerline.length
    route_length = EGO_DIST_BEFORE_JUNC+dist_in_junc+EGO_DIST_BEFORE_JUNC
    timeout = int(SECONDS_GIVEN_PER_METERS * route_length + INITIAL_SECONDS_DELAY)

    sc = []

    sc.append("<?xml version='1.0' encoding='UTF-8'?>\n")
    sc.append("<routes>\n")
    sc.append(f"    <route id='{route_id}' town='{town}' intersection_id='{intersection_id}' timeout='{timeout}'>\n")

    ego = scene.egoObject
    # Actor initializations
    for o in scene.objects:
        pos = scenicToCarlaLocation(o.position, 0.0)
        rot = scenicToCarlaRotation(o.heading)
        man = o.maneuverType

        if o is ego:
            sc.append(f"        <waypoint x='{pos.x}' y='{pos.y}' z='0.0' maneuver='{man}'/>\n")

        else:
            # TODO speed is hard coded for now...
            sc.append(f"        <other_actor x='{pos.x}' y='{pos.y}' z='0.0'  yaw='{rot.yaw}' speed='{'transfuser'}' maneuver='{man}' model='vehicle.tesla.model3'/>\n")

    # sc.append("        <weather id='ClearSunset' cloudiness='20.000000' precipitation='0.000000' precipitation_deposits='50.000000' wind_intensity='0.350000' sun_azimuth_angle='90.000000' sun_altitude_angle='75.000000' fog_density='0.000000' fog_distance='0.000000' fog_falloff='0.000000' wetness='0.000000'/>\n")
    # Below iis the default weather for Town05
    sc.append("        <weather id='Custom' cloudiness='10.000000' precipitation='0.000000' precipitation_deposits='0.000000' wind_intensity='5.000000' sun_azimuth_angle='170.000000' sun_altitude_angle='30.000000' fog_density='10.000000' fog_distance='75.000000' fog_falloff='0.900000' wetness='0.000000'/>\n")

    # CARLA WEATHER PRESETS
    # ClearNoon = WeatherParameters(cloudiness=15.000000, cloudiness=15.000000, precipitation=0.000000, precipitation_deposits=0.000000, wind_intensity=0.350000, sun_azimuth_angle=0.000000, sun_altitude_angle=75.000000, fog_density=0.000000, fog_distance=0.000000, fog_falloff=0.000000, wetness=0.000000)
    # ClearSunset = WeatherParameters(cloudiness=15.000000, cloudiness=15.000000, precipitation=0.000000, precipitation_deposits=0.000000, wind_intensity=0.350000, sun_azimuth_angle=0.000000, sun_altitude_angle=15.000000, fog_density=0.000000, fog_distance=0.000000, fog_falloff=0.000000, wetness=0.000000)
    # CloudyNoon = WeatherParameters(cloudiness=80.000000, cloudiness=80.000000, precipitation=0.000000, precipitation_deposits=0.000000, wind_intensity=0.350000, sun_azimuth_angle=0.000000, sun_altitude_angle=75.000000, fog_density=0.000000, fog_distance=0.000000, fog_falloff=0.000000, wetness=0.000000)
    # CloudySunset = WeatherParameters(cloudiness=80.000000, cloudiness=80.000000, precipitation=0.000000, precipitation_deposits=0.000000, wind_intensity=0.350000, sun_azimuth_angle=0.000000, sun_altitude_angle=15.000000, fog_density=0.000000, fog_distance=0.000000, fog_falloff=0.000000, wetness=0.000000)
    # Default = WeatherParameters(cloudiness=-1.000000, cloudiness=-1.000000, precipitation=-1.000000, precipitation_deposits=-1.000000, wind_intensity=-1.000000, sun_azimuth_angle=-1.000000, sun_altitude_angle=-1.000000, fog_density=-1.000000, fog_distance=-1.000000, fog_falloff=-1.000000, wetness=-1.000000)
    # HardRainNoon = WeatherParameters(cloudiness=90.000000, cloudiness=90.000000, precipitation=60.000000, precipitation_deposits=100.000000, wind_intensity=1.000000, sun_azimuth_angle=0.000000, sun_altitude_angle=75.000000, fog_density=0.000000, fog_distance=0.000000, fog_falloff=0.000000, wetness=0.000000)
    # HardRainSunset = WeatherParameters(cloudiness=80.000000, cloudiness=80.000000, precipitation=60.000000, precipitation_deposits=100.000000, wind_intensity=1.000000, sun_azimuth_angle=0.000000, sun_altitude_angle=15.000000, fog_density=0.000000, fog_distance=0.000000, fog_falloff=0.000000, wetness=0.000000)
    # MidRainSunset = WeatherParameters(cloudiness=80.000000, cloudiness=80.000000, precipitation=30.000000, precipitation_deposits=50.000000, wind_intensity=0.400000, sun_azimuth_angle=0.000000, sun_altitude_angle=15.000000, fog_density=0.000000, fog_distance=0.000000, fog_falloff=0.000000, wetness=0.000000)
    # MidRainyNoon = WeatherParameters(cloudiness=80.000000, cloudiness=80.000000, precipitation=30.000000, precipitation_deposits=50.000000, wind_intensity=0.400000, sun_azimuth_angle=0.000000, sun_altitude_angle=75.000000, fog_density=0.000000, fog_distance=0.000000, fog_falloff=0.000000, wetness=0.000000)
    # SoftRainNoon = WeatherParameters(cloudiness=70.000000, cloudiness=70.000000, precipitation=15.000000, precipitation_deposits=50.000000, wind_intensity=0.350000, sun_azimuth_angle=0.000000, sun_altitude_angle=75.000000, fog_density=0.000000, fog_distance=0.000000, fog_falloff=0.000000, wetness=0.000000)
    # SoftRainSunset = WeatherParameters(cloudiness=90.000000, cloudiness=90.000000, precipitation=15.000000, precipitation_deposits=50.000000, wind_intensity=0.350000, sun_azimuth_angle=0.000000, sun_altitude_angle=15.000000, fog_density=0.000000, fog_distance=0.000000, fog_falloff=0.000000, wetness=0.000000)
    # WetCloudyNoon = WeatherParameters(cloudiness=80.000000, cloudiness=80.000000, precipitation=0.000000, precipitation_deposits=50.000000, wind_intensity=0.350000, sun_azimuth_angle=0.000000, sun_altitude_angle=75.000000, fog_density=0.000000, fog_distance=0.000000, fog_falloff=0.000000, wetness=0.000000)
    # WetCloudySunset = WeatherParameters(cloudiness=90.000000, cloudiness=90.000000, precipitation=0.000000, precipitation_deposits=50.000000, wind_intensity=0.350000, sun_azimuth_angle=0.000000, sun_altitude_angle=15.000000, fog_density=0.000000, fog_distance=0.000000, fog_falloff=0.000000, wetness=0.000000)
    # WetNoon = WeatherParameters(cloudiness=20.000000, cloudiness=20.000000, precipitation=0.000000, precipitation_deposits=50.000000, wind_intensity=0.350000, sun_azimuth_angle=0.000000, sun_altitude_angle=75.000000, fog_density=0.000000, fog_distance=0.000000, fog_falloff=0.000000, wetness=0.000000)
    # WetSunset = WeatherParameters(cloudiness=20.000000, cloudiness=20.000000, precipitation=0.000000, precipitation_deposits=50.000000, wind_intensity=0.350000, sun_azimuth_angle=0.000000, sun_altitude_angle=15.000000, fog_density=0.000000, fog_distance=0.000000, fog_falloff=0.000000, wetness=0.000000)




    sc.append("    </route>\n")
    sc.append("</routes>\n")
    return sc

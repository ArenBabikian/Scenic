

from scenic.simulators.carla.utils.utils import carlaToScenicHeading, carlaToScenicPosition
from utils_geometric import closestDistanceBetweenRectangles
from scenic.core.regions import RectangularRegion
from scenic.simulators.carla.misc import compute_distance
from tools.metrics_log import MetricsLog

import os
import json
import re
import numpy as np
import math
# import carla
import csv
from tqdm import tqdm

def validate_dir(d):
    if not os.path.exists(d):
        print(f"The folder '{d}' does not exist.")
        return

    if not os.path.isdir(d):
        print(f"'{d}' is not a directory.")
        return
    
def validate_path(f):
    if not os.path.exists(f):
        print(f"The file '{f}' does not exist.")
        return

    if not os.path.isfile(f):
        print(f"'{f}' is not a file.")
        return

def iterate_text_files_in_folder(data_sim_dir, abs_scenario_file_dir, measurements_data_path):

    # Validate and get started
    validate_dir(data_sim_dir)
    validate_dir(abs_scenario_file_dir)
    validate_path(measurements_data_path)
    sorted_files = sorted(os.listdir(data_sim_dir))
    with open(measurements_data_path) as j:
        carla_measurements_data = json.load(j)
    

    ###############################################################
    # STEP 1 : FIND GROUND TRUTH EGO PATHS, with ONE actor scenarios
    only_1_actor_scenarios = list(filter(lambda x: '_1ac_' in x, sorted_files))

    # get abstract scenario descriptions file
    with open(f'{abs_scenario_file_dir}/_1actors-abs-scenarios.json') as j:
        abs_scenarios_json = json.load(j)
    
    groundtruth_paths = {mid : {'runs' : {}, 'aggregate_path' : []} for mid in abs_scenarios_json['all_maneuvers']}

    all_paths_coordinates = []

    # get measurements data
    for filename in only_1_actor_scenarios[:]:
        # validation checks
        file_path = os.path.join(data_sim_dir, filename)
        if not(os.path.isfile(file_path) and file_path.endswith(".txt")):
            continue

        # ###### (1) EXTRACT GENERAL INFO FROM FILE NAME
        s = os.path.splitext(os.path.basename(file_path))[0]
        pattern = r"RouteScenario_scen_(\w+)_([0-9]+)_([0-9]+)ac_([0-9]+)_rep([0-9]+)"
        matches = re.search(pattern, s)

        if matches:
            town = matches.group(1)
            junc_id = int(matches.group(2))
            num_actors = int(matches.group(3))
            scenario_instance_id = int(matches.group(4))
            rep_id = int(matches.group(5))
        else:
            exit(f'Error with file: {file_path}')

        # ###### (2) FIND CORRESPONDING ABSTRACT SCENE and EGO MANEUVER
        scen_descs = list(filter(lambda scen : scen['scenario_id'] == scenario_instance_id, abs_scenarios_json['all_scenarios']))
        assert len(scen_descs) == 1
        scen_desc = scen_descs[0]
        ego_maneuver_id = scen_desc['actors'][0]['maneuver']['id']

        # ####### (3) GATHER EXACT MEASUREMENT DATA FROM FILE CONTENTS
        with open(file_path, 'r') as file:
            file_contents = file.read()

        log = MetricsLog(file_contents)
        # get all actors:
        all_actor_ids = log.get_actor_ids_with_type_id('vehicle.tesla.model3')
        assert len(all_actor_ids) == num_actors  # ensure that there is the correct number of actors
        assert all_actor_ids[0] == log.get_ego_vehicle_id() # assert that actor 0 is the ego actor

        # TODO change this to serializable stuff???????
        meas_data = {'transforms' : log._get_all_actor_states(all_actor_ids[0], 'transform'),
                        'control' : log._get_all_actor_states(all_actor_ids[0], 'control')
                        }
        # actor_lights = log._get_all_actor_states(all_actor_ids[0], 'light') # IRRELEVANT

        groundtruth_paths[ego_maneuver_id]['runs'][rep_id] = meas_data

    ###############################################################
    # At this point, we have all the measurement info stored in groundtruth_paths
    # STEP 1.1 : Get some aggregate groundtruth path

    for man_id, details in groundtruth_paths.items():
        all_runs = details['runs']
        assert len(all_runs) == 10

        # TODO also, try to make some measurements as to how varied the ego paths are, like a % or something


        # Calculate the maximum distance between the runs at each timestep
        all_max_distances = []
        max_distances_per_run = {}

        for run1 in all_runs:
            for run2 in all_runs:
                distances = [ego.location.distance(current.location) for ego, current in zip(all_runs[run1]['transforms'], all_runs[run2]['transforms'])]
                all_max_distances.append(max(distances))
                if run1 not in max_distances_per_run:
                    max_distances_per_run[run1] = []
                max_distances_per_run[run1].append(max(distances))
        
        # Maximum distance between all the groundtruth paths
        groundtruth_paths[man_id]['max_distance'] = max(all_max_distances)

        # Find the ID with the lowest maximum value
        # medoid selection
        min_max_id = min(max_distances_per_run, key=lambda k: max(max_distances_per_run[k]))

        # Get the lowest maximum value
        min_max_value = max(max_distances_per_run[min_max_id])

        # Save aggregate path
        groundtruth_paths[man_id]['aggregate_path'] = all_runs[min_max_id]
        groundtruth_paths[man_id]['meadian_path_max_distance'] = min_max_value

        # Save the coordinates of the aggregate path
        all_paths_coordinates.extend([
            {
                'town': town,
                'junction_id': junc_id,
                'num_actors': num_actors,
                'scenario_instance_id': scenario_instance_id,
                'rep_id': rep_id,
                'aggregate': rep_id == min_max_id,
                'man_id': man_id,
                'actor_id': 0,
                'frame': frame_i,
                'x': ego_tr_at_i.location.x,
                'y': ego_tr_at_i.location.y,
                'z': ego_tr_at_i.location.z,
                'pitch': ego_tr_at_i.rotation.pitch,
                'yaw': ego_tr_at_i.rotation.yaw,
                'roll': ego_tr_at_i.rotation.roll
            }
            for rep_id, run_data in all_runs.items()
            for frame_i, ego_tr_at_i in enumerate(run_data['transforms'])
        ])

    ###############################################################
    # STEP 2 : Handle 2-3-4 actor scenario data
    more_actors_scenarios = list(filter(lambda x: '_1ac_' not in x, sorted_files))

    # get measurements data
    data_for_figures = {'map_name' : town, 'junction_id' : junc_id, 'scenarios' : {1:{}, 2:{}, 3:{}, 4:{}}}
    aggregate_data = {}
    for filename in tqdm(more_actors_scenarios[:]):

        # validation checks
        file_path = os.path.join(data_sim_dir, filename)
        if not(os.path.isfile(file_path) and file_path.endswith(".txt")):
            continue

        # ###### (1) EXTRACT GENERAL INFO FROM FILE NAME
        s = os.path.splitext(os.path.basename(file_path))[0]
        pattern = r"RouteScenario_scen_(\w+)_([0-9]+)_([0-9]+)ac_([0-9]+)_rep([0-9]+)"
        matches = re.search(pattern, s)

        if matches:
            town = matches.group(1)
            junc_id = int(matches.group(2))
            num_actors = int(matches.group(3))
            scenario_instance_id = int(matches.group(4))
            rep_id = int(matches.group(5))
        else:
            exit(f'Error with file: {file_path}')

        # ###### (2) FIND CORRESPONDING ABSTRACT SCENE and EGO MANEUVER
        with open(f'{abs_scenario_file_dir}/_{num_actors}actors-abs-scenarios.json') as j:
            abs_scenarios_json = json.load(j)

        scen_descs = list(filter(lambda scen : scen['scenario_id'] == scenario_instance_id, abs_scenarios_json['all_scenarios']))
        assert len(scen_descs) == 1
        scen_desc = scen_descs[0]

        # ###### (3) GET GROUNDTRUTH EGO PATH
        ego_maneuver_id = scen_desc['actors'][0]['maneuver']['id']
        gt_ego_path = groundtruth_paths[ego_maneuver_id]['aggregate_path']
        gt_max_distance = groundtruth_paths[ego_maneuver_id]['max_distance']
        gt_meadian_path_max_distance = groundtruth_paths[ego_maneuver_id]['meadian_path_max_distance']

        # ###### (4) GET CURRENT EGO PATH (from the current run)
        with open(file_path, 'r') as file:
            file_contents = file.read()

        log = MetricsLog(file_contents)
        # get all actors:
        all_actor_ids = log.get_actor_ids_with_type_id('vehicle.tesla.model3')
        assert len(all_actor_ids) == num_actors  # ensure that there is the correct number of actors
        assert all_actor_ids[0] == log.get_ego_vehicle_id() # assert that actor 0 is the ego actor
        ego_id = all_actor_ids[0]

        # ego path
        current_ego_path = {'transforms' : log._get_all_actor_states(ego_id, 'transform'),
                        'control' : log._get_all_actor_states(ego_id, 'control')
                        }
        
        # other vehicle paths
        other_vehicle_paths = {}
        carlaId2specId = {}
        for other_spec_id, other_carla_id in enumerate(all_actor_ids[1:]):
            carlaId2specId[other_carla_id] = other_spec_id
            other_vehicle_paths[other_carla_id] = {'transforms' : log._get_all_actor_states(other_carla_id, 'transform'),
                        'control' : log._get_all_actor_states(other_carla_id, 'control')
                        }
            
        # ###### (5) GATHER RELEVANT DATA

        # (A) prep runtimes gathering
        all_records = carla_measurements_data['_checkpoint']['records']

        route_id_in_meas = f'RouteScenario_scen_{town}_{junc_id}_{num_actors}ac_{scenario_instance_id}'
        record_infos = list(filter(lambda r : r['route_id'] == route_id_in_meas and r['index'] % 10 == rep_id, all_records))
        assert len(record_infos) == 1
        record_info = record_infos[0]

        # (B) EGO Does scenario succeed?
        status = record_info['status']
        
        # (C) EGO Is there a collision?
        # NOTE, there is at most 1 collision during a run
        collisions = log.get_actor_collisions(ego_id)

        # (D) EGO Is there a near-miss situation?
        # TODO include which other vehicle there was a near-miss
        near_misses = [0 for _ in other_vehicle_paths]
        # iterate through all scenes
        for normalized_id, other_vehicle_id in enumerate(other_vehicle_paths):
            other_vehicle_path = other_vehicle_paths[other_vehicle_id]

            for frame_i, ego_tr_at_i in enumerate(current_ego_path['transforms']):
                other_tr_at_i = other_vehicle_path['transforms'][frame_i]

                # EGO
                ego_vec = carlaToScenicPosition(ego_tr_at_i.location)
                ego_head = carlaToScenicHeading(ego_tr_at_i.rotation)
                ego_region = RectangularRegion(ego_vec, ego_head, 2, 4.5)

                # OTHER
                other_vec = carlaToScenicPosition(other_tr_at_i.location)
                other_head = carlaToScenicHeading(other_tr_at_i.rotation)
                other_region = RectangularRegion(other_vec, other_head, 2, 4.5)

                distance_between_ego_and_other = closestDistanceBetweenRectangles(ego_region, other_region)

                DISTANCE_THRESHOLD = 1.0
                if distance_between_ego_and_other < DISTANCE_THRESHOLD:
                    # found a near-miss situation with the current other vehicle
                    near_misses[normalized_id] = 1

                    # move on to the next other vehicle
                    break

        # (E) Is the collision avoidable/preventable?
        # TODO TODO TODO




        # (F) Preventative Measures per frame
        PREVENTITIVE_THRESHOLD = 5
        matching_points_per_frame = np.zeros(len(gt_ego_path['transforms']))
        # matching_points_per_frame = np.array([0] * len(gt_ego_path['transforms']))

        current_path_coordinates = []
        # find closest point on gt_ego_path to current_ego_path at all frames
        # also save coordinates of the path
        for frame_i, ego_tr_at_i in enumerate(current_ego_path['transforms']):
            # find closest point on gt_ego_path to ego_tr_at_i
            # ego_location = carlaToScenicPosition(ego_tr_at_i.location)
            # ego_rotation = carlaToScenicHeading(ego_tr_at_i.rotation)
            distances = [gt_tr.location.distance(ego_tr_at_i.location) for gt_tr in gt_ego_path['transforms']]
            
            # Find the index of the closest point (min distance)
            closest_point_id = distances.index(min(distances))

            matching_points_per_frame[closest_point_id] += 1
            
            coord = {}
            coord['town'] = town
            coord['junction_id'] = junc_id
            coord['num_actors'] = num_actors
            coord['scenario_instance_id'] = scenario_instance_id
            coord['rep_id'] = rep_id
            coord['aggregate'] = False
            coord['man_id'] = ego_maneuver_id
            coord['actor_id'] = 0
            coord['frame'] = frame_i
            coord['x'] = ego_tr_at_i.location.x
            coord['y'] = ego_tr_at_i.location.y
            coord['z'] = ego_tr_at_i.location.z
            coord['pitch'] = ego_tr_at_i.rotation.pitch
            coord['yaw'] = ego_tr_at_i.rotation.yaw
            coord['roll'] = ego_tr_at_i.rotation.roll

            all_paths_coordinates.append(coord)
        
        # count number of frames in gt_ego_path, which have more matching points, than the previous frame + PREVENTITIVE_THRESHOLD
        # this indicates a slow down in the ego vehicle
        number_of_preventitive_maneuvers = len(np.where(matching_points_per_frame[:-1] <= matching_points_per_frame[1:] - PREVENTITIVE_THRESHOLD)[0])

        # we compare with `gt_ego_path`
        all_max_distances = []
        for ego_path in groundtruth_paths[ego_maneuver_id]['runs'].values():
            distances = [ego.location.distance(current.location) for ego, current in zip(ego_path['transforms'], current_ego_path['transforms'])]
            all_max_distances.append(max(distances))
        deviation_from_closest_gt = min(all_max_distances)
        deviation_from_closest_gt_ratio = deviation_from_closest_gt / gt_max_distance

        # Max deviation from gt_ego_path
        deviation_from_median_gt = max([ego.location.distance(current.location) for ego, current in zip(gt_ego_path['transforms'], current_ego_path['transforms'])])
        deviation_from_median_gt_ratio = deviation_from_median_gt / gt_meadian_path_max_distance

        # (G) NONEGO Does scenario have a nonego collision?
        nonego_collision = False
        for nonego_id in all_actor_ids[1:]:
            collisions = log.get_actor_collisions(nonego_id)
            for frame, colliding_ids in collisions.items():
                if any(actor_id in colliding_ids for actor_id in all_actor_ids[1:]):
                    nonego_collision = True
                    break
            if nonego_collision:
                break

        # (B) Collision info
        # Note, there is at most 1 collision during a run
        collisions = log.get_actor_collisions(ego_id)

        # (B) Near-miss info
        # TODO include which other vehicle there was a near-miss
        near_misses = [0 for _ in other_vehicle_paths]
        # iterate through all scenes
        for normalized_id, other_vehicle_id in enumerate(other_vehicle_paths):
            other_maneuver_id = scen_desc['actors'][normalized_id + 1]['maneuver']['id']
            other_vehicle_path = other_vehicle_paths[other_vehicle_id]

            for frame_i, ego_tr_at_i in enumerate(current_ego_path['transforms']):
                other_tr_at_i = other_vehicle_path['transforms'][frame_i]

                # EGO
                ego_vec = carlaToScenicPosition(ego_tr_at_i.location)
                ego_head = carlaToScenicHeading(ego_tr_at_i.rotation)
                ego_region = RectangularRegion(ego_vec, ego_head, 2, 4.5)

                # OTHER
                other_vec = carlaToScenicPosition(other_tr_at_i.location)
                other_head = carlaToScenicHeading(other_tr_at_i.rotation)
                other_region = RectangularRegion(other_vec, other_head, 2, 4.5)

                distance_between_ego_and_other = closestDistanceBetweenRectangles(ego_region, other_region)

                DISTANCE_THRESHOLD = 1.0
                if distance_between_ego_and_other < DISTANCE_THRESHOLD:
                    # found a near-miss situation with the current other vehicle
                    near_misses[normalized_id] = 1

                    # move on to the next other vehicle
                    break
            
                coord = {}
                coord['town'] = town
                coord['junction_id'] = junc_id
                coord['num_actors'] = num_actors
                coord['scenario_instance_id'] = scenario_instance_id
                coord['rep_id'] = rep_id
                coord['aggregate'] = False
                coord['man_id'] = other_maneuver_id
                coord['actor_id'] = other_vehicle_id
                coord['frame'] = frame_i
                coord['x'] = ego_tr_at_i.location.x
                coord['y'] = ego_tr_at_i.location.y
                coord['z'] = ego_tr_at_i.location.z
                coord['pitch'] = other_tr_at_i.rotation.pitch
                coord['yaw'] = other_tr_at_i.rotation.yaw
                coord['roll'] = other_tr_at_i.rotation.roll

                all_paths_coordinates.append(coord)

        # (7) Do we disregard the scenario?
        if num_actors not in aggregate_data:
            aggregate_data[num_actors] = {
                'status': {
                    'Completed': 0,
                    'Failed': 0,
                    'Failed - Agent timed out': 0
                },
                'nonego_collision': {
                    'True': 0,
                    'False': 0
                },
                'total_scenarios': 0
            }
        aggregate_data[num_actors]['status'][status] += 1
        aggregate_data[num_actors]['nonego_collision'][str(nonego_collision)] += 1
        aggregate_data[num_actors]['total_scenarios'] += 1




        # ###### (6) SAVE THE COOKED DATA
        # BIG TODOs HERE
        data_for_this_scenario_execution = {'runtime_in_game':record_info['meta']['duration_game'],
                                            'runtime_system_time': record_info['meta']['duration_system'],
                                            'deviation_from_closest_gt' : deviation_from_closest_gt,
                                            'deviation_from_closest_gt_ratio' : deviation_from_closest_gt_ratio,
                                            'deviation_from_median_gt' : deviation_from_median_gt,
                                            'deviation_from_median_gt_ratio' : deviation_from_median_gt_ratio,
                                            'collided with' : collisions,
                                            'num_preventative_maneuver' : number_of_preventitive_maneuvers,
                                            'near_miss_with' : near_misses
                               }

                               

        # ###### (5.1) ADDITIONAL MEASUREMENT ANALYSIS FOR 2-ACTOR SCENES
        if num_actors == 2:
            concrete_relative_statistics_sequence = {'distances':[],
                                                     'ego_to_other_angles':[],
                                                     'other_to_ego_angles':[]
                                                     }
            # Save the relative positions and heading angles  between the ego and the non-ego at each frame

            assert len(other_vehicle_paths.values()) == 1
            nonego_path = list(other_vehicle_paths.values())[0]

            assert len(current_ego_path['transforms']) == len(nonego_path['transforms'])

            for frame_i, ego_transform_at_i in enumerate(current_ego_path['transforms']):
                nonego_transform_at_i = nonego_path['transforms'][frame_i]

                ego_loc = ego_transform_at_i.location
                ego_rot = ego_transform_at_i.rotation
                nonego_loc = nonego_transform_at_i.location
                nonego_rot = nonego_transform_at_i.rotation

                def viewAngleToPoint(point, base, heading):
                    x, y = base.x, base.y
                    ox, oy = point.x, point.y
                    h = math.radians(heading.yaw)
                    angle= math.atan2(oy - y, ox - x) - (h + (math.pi / 2.0))

                    while angle > math.pi:
                        angle -= math.tau
                    while angle < -math.pi:
                        angle += math.tau
                    assert -math.pi <= angle <= math.pi
                    return math.degrees(angle)

                # DISTANCE
                distance = compute_distance(ego_loc, nonego_loc)
                concrete_relative_statistics_sequence['distances'].append(distance)

                # EGO-OTHER ANGLE
                # where is other in the vision plane of ego?
                # (0 = other is ahead, +/-180 = other is behind)
                a1 = viewAngleToPoint(nonego_loc, ego_loc, ego_rot)
                concrete_relative_statistics_sequence['ego_to_other_angles'].append(a1)
                # TODO get corners, then get angle range

                # OTHER-EGO ANGLLE.
                # What part of the other vehicle is ego seeing?
                # (0 = front of other, +/-180 = back of other)
                a2 = viewAngleToPoint(ego_loc, nonego_loc, nonego_rot)
                concrete_relative_statistics_sequence['other_to_ego_angles'].append(a2)

            data_for_this_scenario_execution['relative_stats'] = concrete_relative_statistics_sequence

        if scenario_instance_id not in data_for_figures['scenarios'][num_actors]:
            data_for_figures['scenarios'][num_actors][scenario_instance_id] = {}
        data_for_figures['scenarios'][num_actors][scenario_instance_id][rep_id] = data_for_this_scenario_execution

    # (8) Print preliminary measurement info
    for num_actors, data in aggregate_data.items():
        print(f"Num Actors: {num_actors}")
        print(f"Status: {data['status']}")
        print(f"Nonego Collision: {data['nonego_collision']}")
        print()
    # for given size, tot_num scenarios, num_successes, num_failures, num_failures_with_nonego_collision

    return data_for_figures, all_paths_coordinates


def main():
    # Set the folder path here
    data_path = "fse/data-sim/Town05_2240"
    # data_path = "fse/data-sim/Town04_916"
    sim_data_dir = f'{data_path}/txt'
    abs_scenario_dir = f'{data_path}/abs_scenarios'
    measurements_dat_path = f'{data_path}/log/measurements.json'
    out_path = f'{data_path}/cooked_measurements.json'
    coords_out_path = f'{data_path}/path_coords.json'
    
    # Get the list of file contents
    file_contents_list, paths_coordinates = iterate_text_files_in_folder(sim_data_dir, abs_scenario_dir, measurements_dat_path)

    # Save the list as a JSON file
    with open(out_path, "w") as json_file:
        json.dump(file_contents_list, json_file, indent=4)
    print(f'Saved cooked measurments at     {out_path}')

    # Save the coordinates as a JSON file
    with open(coords_out_path, "w") as json_file:
        json.dump(paths_coordinates, json_file, indent=4)
    print(f'Saved coordinates at            {coords_out_path}')

    # Save the coordinates as a CSV file
    # Define the fields/columns for the CSV file
    fields = ['town', 'junction_id', 'num_actors', 'scenario_instance_id', 'rep_id', 'aggregate', 'man_id', 'actor_id', 'frame', 'x', 'y', 'z', 'pitch', 'yaw', 'roll']

    # Open the CSV file with write permission
    csv_out_path = coords_out_path.replace('.json', '.csv')
    with open(csv_out_path, "w", newline="") as csvfile:
        # Create a CSV writer using the field/column names
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        
        # Write the header row (column names)
        writer.writeheader()
        
        # Write the data
        for row in paths_coordinates:
            writer.writerow(row)
    print(f'Saved coordinates at            {csv_out_path}')

if __name__ == "__main__":
    main()

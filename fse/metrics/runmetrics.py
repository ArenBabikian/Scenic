

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
import carla

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

        # TODO aggregation, medoid selection
        agg_run_data = all_runs[0] # TEMPORARY TODO

        # TODO also, try to make some measurements as to how varied the ego paths are, like a % or something

        # Save aggregate path
        groundtruth_paths[man_id]['aggregate_path'] = agg_run_data

    ###############################################################
    # STEP 2 : Handle 2-3-4 actor scenario data
    more_actors_scenarios = list(filter(lambda x: '_1ac_' not in x, sorted_files))

    # get measurements data
    data_for_figures = {'map_name' : town, 'junction_id' : junc_id, 'scenarios' : {1:{}, 2:{}, 3:{}, 4:{}}}
    for filename in more_actors_scenarios[:]:

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

        # (B) Preventative Measures per frame
        # TODO Attila

        # (B) Collision info
        # Note, there is at most 1 collision during a run
        collisions = log.get_actor_collisions(ego_id)

        # (B) Near-miss info
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

        # TODO TODO TODO TODO TODO TODO TODO TODO
        # check somehow that non-egos are not colliding with eavh other, which invalisdates the scenario


        # (B) Compare gt_ego_path to current_ego_path


        # ###### (6) SAVE THE COOKED DATA
        # BIG TODOs HERE
        data_for_this_scenario_execution = {'runtime_in_game':record_info['meta']['duration_game'],
                                            'runtime_system_time': record_info['meta']['duration_system'],
                                            'collided with' : collisions,
                                            'num_preventative_maneuver' : -1,
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

    return data_for_figures


def main():
    # Set the folder path here
    data_path = "fse/data-sim/Town05_2240"
    sim_data_dir = f'{data_path}/txt'
    abs_scenario_dir = f'{data_path}/abs_scenarios'
    measurements_dat_path = f'{data_path}/log/measurements.json'
    out_path = f'{data_path}/cooked_measurements.json'
    
    # Get the list of file contents
    file_contents_list = iterate_text_files_in_folder(sim_data_dir, abs_scenario_dir, measurements_dat_path)

    # Save the list as a JSON file
    with open(out_path, "w") as json_file:
        json.dump(file_contents_list, json_file, indent=4)
    print(f'Saved cooked measurments at     {out_path}')

if __name__ == "__main__":
    main()

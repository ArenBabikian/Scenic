

from runmetrics import validate_dir, validate_path
import os
import json

def gen_figures(cooked_measurements_path, abs_scenario_dir, included_sizes):

    # Validate and get started
    validate_dir(abs_scenario_dir)
    validate_path(cooked_measurements_path)
    with open(cooked_measurements_path) as j:
        cooked_measurements = json.load(j)

    included_sizes = [3]

    # SEMANTICS
    # >> ego-related measurements:
    #   semantics are the same regardless of the number of non-ego actors
    # >> non-ego-related measurements:
    #   for 2-actor scenarios:
    #     there is 1 non-ego, s the metric is whether that one is satisfying the criterion (e.g. if that one has the specified maneuver type)
    #   for 3/4-actor scenarios:
    #     ...TODO



    # DATA DICTIONARIES
    # EGO
    map_ego____specific_man = {}
    map_ego____type_____man = {}
    map_ego____start___lane = {}
    map_ego____end_____lane = {}

    # NON_EGO
    map_nonego_specific_man = {}
    map_nonego_type_____man = {}
    map_nonego_start___lane = {}
    map_nonego_end_____lane = {}

    # RELATIONSHIPS
    map_init__relationship = {}
    map_final_relationship = {}

    all_scenarios = cooked_measurements['scenarios']
    for num_actors in all_scenarios:
        if int(num_actors) not in included_sizes:
            continue

        # ABSTRACT
        with open(f'{abs_scenario_dir}/_{num_actors}actors-abs-scenarios.json') as j:
            abs_scenarios_json = json.load(j)

        all_scenarios_at_size = all_scenarios[num_actors]
        for scenario_spec_id in all_scenarios_at_size:
            all_reps_for_scenario_spec = all_scenarios_at_size[scenario_spec_id]

            # ABSTRACT INFO ABOUT THE REP
            scen_descs = list(filter(lambda scen : scen['scenario_id'] == int(scenario_spec_id), abs_scenarios_json['all_scenarios']))
            assert len(scen_descs) == 1
            abs_scen_info = scen_descs[0]

            for rep_id  in all_reps_for_scenario_spec:

                # GATHERED INFO ABOUT THE REP
                rep_info = all_reps_for_scenario_spec[rep_id]
                # print(rep_info)
                num_collisions = len(rep_info['collided with'])
                assert num_collisions < 2

                # GATHER SPECIFIC INFO (2 actors only, for now)
                # EGO
                data_ego____specific_man = abs_scen_info['actors'][0]['maneuver']['id']
                data_ego____type_____man = abs_scen_info['actors'][0]['maneuver']['type']
                data_ego____start___lane = abs_scen_info['actors'][0]['maneuver']['start_lane_id']
                data_ego____end_____lane = abs_scen_info['actors'][0]['maneuver']['end_lane_id']

                add_data_to_map(data_ego____specific_man, map_ego____specific_man, num_collisions)
                add_data_to_map(data_ego____type_____man, map_ego____type_____man, num_collisions)
                add_data_to_map(data_ego____start___lane, map_ego____start___lane, num_collisions)
                add_data_to_map(data_ego____end_____lane, map_ego____end_____lane, num_collisions)

                # NON-EGO
                data_nonego_specific_man = abs_scen_info['actors'][1]['maneuver']['id']
                data_nonego_type_____man = abs_scen_info['actors'][1]['maneuver']['type']
                data_nonego_start___lane = abs_scen_info['actors'][1]['maneuver']['start_lane_id']
                data_nonego_end_____lane = abs_scen_info['actors'][1]['maneuver']['end_lane_id']

                add_data_to_map(data_nonego_specific_man, map_nonego_specific_man, num_collisions)
                add_data_to_map(data_nonego_type_____man, map_nonego_type_____man, num_collisions)
                add_data_to_map(data_nonego_start___lane, map_nonego_start___lane, num_collisions)
                add_data_to_map(data_nonego_end_____lane, map_nonego_end_____lane, num_collisions)

                # RELATIONSHIP
                data_init__relationship = abs_scen_info['initial_relations']['0']['1']
                data_final_relationship = abs_scen_info['final_relations']['0']['1']
                add_data_to_map(data_init__relationship, map_init__relationship, num_collisions)
                add_data_to_map(data_final_relationship, map_final_relationship, num_collisions)

    all_relevant_maps = {'ego____specific' : map_ego____specific_man,
                         'ego________type' : map_ego____type_____man,
                         'ego_______start' : map_ego____start___lane,
                         'ego_________end' : map_ego____end_____lane,

                         'nonego_specific' : map_nonego_specific_man,
                         'nonego_____type' : map_nonego_type_____man,
                         'nonego____start' : map_nonego_start___lane,
                         'nonego______end' : map_nonego_end_____lane,

                         'rel________init' : map_init__relationship,
                         'rel_______final' : map_final_relationship
    }

    for map_id in all_relevant_maps:
        print('---------------------')
        print(f'<<<{map_id}>>>')
        for x in all_relevant_maps[map_id]:
            print(f'{x} : {all_relevant_maps[map_id][x]}')
    

def add_data_to_map(data, data2metric, num_collisions):
    if data not in data2metric:
        data2metric[data] = {'attempts' : 0, 'collisions' : 0}
    data2metric[data]['attempts'] += 1
    data2metric[data]['collisions'] += num_collisions


def main():
    data_path = "fse/data-sim/Town05_2240" # Attila, modify this
    cooked_measurements_path = f'{data_path}/cooked_measurements.json'
    abs_scenario_dir = f'{data_path}/abs_scenarios'
    included_sizes = [3]
    
    # Get the list of file contents
    data = gen_figures(cooked_measurements_path, abs_scenario_dir, included_sizes)

    # Save the list as a JSON file
    # with open(out_path, "w") as json_file:
    #     json.dump(file_contents_list, json_file, indent=4)
    # print(f'Saved cooked measurments at     {out_path}')

if __name__ == "__main__":
    main()

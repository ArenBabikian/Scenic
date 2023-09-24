

from runmetrics import validate_dir, validate_path
import os
import json

def gen_figures(cooked_measurements_path, abs_scenario_dir, included_sizes):

    # Validate and get started
    validate_dir(abs_scenario_dir)
    validate_path(cooked_measurements_path)
    with open(cooked_measurements_path) as j:
        cooked_measurements = json.load(j)

    # SEMANTICS
    # >> ego-related measurements:
    #   semantics are the same regardless of the number of non-ego actors
    # >> non-ego-related measurements:
    #   for 2-actor scenarios:
    #     there is 1 non-ego, so the metric is whether that one is satisfying the criterion (e.g. if that one has the specified maneuver type)
    #   for 3/4-actor scenarios:
    #     if any of the non-egos is satisfying the criterion
    # >> relationship measurements:
    #   for 2-actor scenarios:
    #     if the non-ego satisfies the positional relation constraint
    #   for 3/4-actor scenarios:
    #     if any of the non-egos satisfy the positional relatio constraint WRT the EGO

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
                num_collisions = len(rep_info['collided with'])
                assert num_collisions < 2

                near_miss_occurance = 1 if sum(rep_info['near_miss_with']) else 0

                stats_to_add = {'collisions':num_collisions, 'near-miss':near_miss_occurance}
                

                # GATHER SPECIFIC INFO (2 actors only, for now)
                # EGO
                data_ego____specific_man = abs_scen_info['actors'][0]['maneuver']['id']
                data_ego____type_____man = abs_scen_info['actors'][0]['maneuver']['type']
                data_ego____start___lane = abs_scen_info['actors'][0]['maneuver']['start_lane_id']
                data_ego____end_____lane = abs_scen_info['actors'][0]['maneuver']['end_lane_id']

                add_data_to_map(data_ego____specific_man, map_ego____specific_man, stats_to_add)
                add_data_to_map(data_ego____type_____man, map_ego____type_____man, stats_to_add)
                add_data_to_map(data_ego____start___lane, map_ego____start___lane, stats_to_add)
                add_data_to_map(data_ego____end_____lane, map_ego____end_____lane, stats_to_add)

                # iterate through NON-EGOs
                for nonego_actor in abs_scen_info['actors'][1:]:
                    data_nonego_specific_man = nonego_actor['maneuver']['id']
                    data_nonego_type_____man = nonego_actor['maneuver']['type']
                    data_nonego_start___lane = nonego_actor['maneuver']['start_lane_id']
                    data_nonego_end_____lane = nonego_actor['maneuver']['end_lane_id']
                    add_data_to_map(data_nonego_specific_man, map_nonego_specific_man, stats_to_add)
                    add_data_to_map(data_nonego_type_____man, map_nonego_type_____man, stats_to_add)
                    add_data_to_map(data_nonego_start___lane, map_nonego_start___lane, stats_to_add)
                    add_data_to_map(data_nonego_end_____lane, map_nonego_end_____lane, stats_to_add)

                # iterate through INITIAL RELATIONS, only relative to ego
                all_initial_relations_from_ego = abs_scen_info['initial_relations']['0']
                for target in all_initial_relations_from_ego:
                    data_init__relationship = all_initial_relations_from_ego[target]
                    add_data_to_map(data_init__relationship, map_init__relationship, stats_to_add)

                # iterate through FINAL RELATIONS, only relative to ego
                all_final_relations_from_ego = abs_scen_info['final_relations']['0']
                for target in all_final_relations_from_ego:
                    data_final_relationship = all_final_relations_from_ego[target]
                    add_data_to_map(data_final_relationship, map_final_relationship, stats_to_add)


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

    return all_relevant_maps
    

def add_data_to_map(data, data2metric, stats_to_add):
    if data not in data2metric:
        data2metric[data] = {'attempts' : 0, 'collisions' : 0, '>0-near-miss-occured' : 0}
    data2metric[data]['attempts'] += 1
    data2metric[data]['collisions'] += stats_to_add['collisions']
    data2metric[data]['>0-near-miss-occured'] += stats_to_add['near-miss']


def main():
    data_path = "fse/data-sim/Town05_2240" # Attila, modify this
    cooked_measurements_path = f'{data_path}/cooked_measurements.json'
    abs_scenario_dir = f'{data_path}/abs_scenarios'
    included_sizes = [2, 3, 4]
    
    # Get the list of file contents
    data = gen_figures(cooked_measurements_path, abs_scenario_dir, included_sizes)

    # PRINT DATA
    print('_______________________________________')
    print(F'AGGREGATE RESULTS FOR {included_sizes}')

    for map_id in data:
        print('---------------------')
        print(f'<<<{map_id}>>>')
        for x in data[map_id]:
            print(f'{x} : {data[map_id][x]}')

    # Save the list as a JSON file
    # with open(out_path, "w") as json_file:
    #     json.dump(file_contents_list, json_file, indent=4)
    # print(f'Saved cooked measurments at     {out_path}')

if __name__ == "__main__":
    main()

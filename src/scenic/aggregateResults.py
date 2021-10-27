
import subprocess
import statistics
import os
import json

maps = ['tram05']
configurations = ['2actors', '3actors', '4actors']
num_scenes = 5 #20
approaches = ['sc1', 'sc2', 'sc3', 'nsga']

data = {}
for m in maps:
    data[m] = {}
    for config in configurations:
        data[m][config] = {}
        for approach in approaches:
            current_data = {}
            num_attempts = 0
            num_successes = 0
            all_times = []
            # NSGA
            all_nsga_succ_percentages = []

            # Scenic
            num_removed_succ = 0
            all_removed_succ_percentages = []

            for i in range(num_scenes):
                json_path = f'measurements/results/{m}/{config}/{i}-0/d-{approach}/_measurementstats.json'
                if os.path.exists(json_path):
                    with open(json_path) as f:
                        json_data = json.load(f)
                    
                    json_res = json_data['results']
                    num_attempts += len(json_res)

                    for r in json_res:
                        if r['success']:
                            num_successes += 1
                            all_times.append(r['time'])

                            if approach != 'nsga':
                                if r['num_rm_con'] == r['num_sat_rm_con']:
                                    num_removed_succ += 1
                                if r['num_rm_con'] != 0:
                                    all_removed_succ_percentages.append(r['num_sat_rm_con']/r['num_rm_con'])
                        
                        if approach == 'nsga':
                            if r['num_con'] != 0:
                                all_nsga_succ_percentages.append(r['num_sat_con']/r['num_con'])
            
            current_data['total_attempts'] = num_attempts
            current_data['total_successes'] = num_successes
            p = -1 if num_attempts == 0 else num_successes / num_attempts
            current_data['percentage_succ'] = p
            median = -1 if not all_times else statistics.median(all_times)
            current_data['median_time_of_success'] = median
            
            if approach == 'nsga':
                median2 = -1 if not all_nsga_succ_percentages else statistics.mean(all_nsga_succ_percentages)
                current_data['NS_average_percentage_of_sat'] = median2
            else:
                current_data['SC_total_succ_and_removed_sat'] = num_removed_succ
                p2 = -1 if num_attempts == 0 else num_removed_succ / num_attempts
                current_data['SC_percentage_succ_and_removed_sat'] = p2
                median2 = -1 if not all_removed_succ_percentages else statistics.median(all_removed_succ_percentages)
                current_data['SC_median_percentage_of_removed_sat'] = median2


            data[m][config][approach] = current_data

out_path = 'measurements/results/aggregate.json'
with open(out_path, 'w') as outfile:
    json.dump(data, outfile, indent=4)

print(f'Saved aggregate measurement stats at {out_path}')


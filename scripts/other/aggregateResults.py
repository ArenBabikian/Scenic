
from copy import Error
import statistics
import os
import json
from pathlib import Path

maps = ['tram05', 'town02', 'zalafullcrop']
configurations = ['2actors', '3actors', '4actors']
num_scenes = range(0, 20) #range(20)
approaches = ['sc1', 'sc2', 'sc3', 'nsga']

# history_times = [30, 60, 120, 180, 300, 600, 1200, 1800, 2400, 3000]
history_times = [30, 60, 120, 180, 240, 300, 360, 420, 480, 540, 600]
tolerance = 1

data_dir = 'measurements/data'
src_dir = 'measurements/results'
out_dir = f'{src_dir}/aggregate'
Path(f'{out_dir}/').mkdir(parents=True, exist_ok=True)

data = {}
for m in maps:
    data[m] = {}
    for config in configurations:
        data[m][config] = {}
        gen_base_path = f'{data_dir}/{m}/{config}/'
        gen_stats_path = gen_base_path+'_genstats.json'
        if not os.path.isfile(gen_stats_path):
            continue

        with open(gen_stats_path) as f:
            gen_stats_data = json.load(f)
        for approach in approaches:
            current_data = {}
            scenes_count = 0
            num_attempts = 0
            num_successes = 0
            all_times = []
            fail_times = []

            all_num_cons = []
            all_num_hard_cons = []
            all_num_soft_cons = []
            all_num_removed_cons = []
            # NSGA
            nsga_s1_con_sat_perc = []
            nsga_s1_con_hard_sat_perc = []
            nsga_s1_con_soft_sat_perc = []
            nsga_s2_con_sat_perc = []
            nsga_s2_con_hard_sat_perc = []
            nsga_s2_con_soft_sat_perc = []
            history_failures = [ 0 for _ in history_times]
            history_con_sat_perc = [ [] for _ in history_times]
            history_con_soft_sat_perc = [ [] for _ in history_times]
            history_con_hard_sat_perc = [ [] for _ in history_times]

            # Scenic
            num_removed_succ = 0
            all_removed_succ_percentages = []

            found_at_least_one_measurement = False

            for i in num_scenes:
                json_path = f'{src_dir}/{m}/{config}/{i}-0/d-{approach}/_measurementstats.json'
                if os.path.exists(json_path):
                    found_at_least_one_measurement = True
                    with open(json_path) as f:
                        json_data = json.load(f)
                    
                    json_res = json_data['results']
                    if len(json_res) > 0:
                        scenes_count += 1
                    num_attempts += len(json_res)

                    for r in json_res:
                        if r['success']:
                            num_successes += 1
                            all_times.append(r['time'])

                            # num_iterations ignored for now

                            if approach != 'nsga':
                                if r['CON_sat_%_rm'] == 1:
                                    num_removed_succ += 1
                                if r['CON_sat_%_rm'] != -1:
                                    all_removed_succ_percentages.append(r['CON_sat_%_rm'])
                        else:
                            fail_times.append(r['time'])

                        
                        if approach == 'nsga':
                            # andling the 2 solutions
                            s1 = r['solutions']['sol_best_global']
                            if s1['CON_sat_%'] != -1:
                                nsga_s1_con_sat_perc.append(s1['CON_sat_%'])
                            if s1['CON_sat_%_hard'] != -1:
                                nsga_s1_con_hard_sat_perc.append(s1['CON_sat_%_hard'])
                            if s1['CON_sat_%_soft'] != -1:
                                nsga_s1_con_soft_sat_perc.append(s1['CON_sat_%_soft'])

                            s2 = r['solutions']['sol_best_Hard_Prio']
                            if s2['CON_sat_%'] != -1:
                                nsga_s2_con_sat_perc.append(s2['CON_sat_%'])
                            if s2['CON_sat_%_hard'] != -1:
                                nsga_s2_con_hard_sat_perc.append(s2['CON_sat_%_hard'])
                            if s2['CON_sat_%_soft'] != -1:
                                nsga_s2_con_soft_sat_perc.append(s2['CON_sat_%_soft'])

                            # Handling history
                            if 'history' in r:
                                h_sols_map = r['history']
                                t_ind = 0
                                for h_time in reversed(list(h_sols_map.keys())):
                                    h_t = float(h_time)
                                    expected_t = history_times[t_ind]
                                    if h_t > expected_t + tolerance:
                                        raise ValueError(f'expecting time {expected_t}, got time {h_t}')

                                    h_bestSol = h_sols_map[h_time]['sol_best_global']
                                    history_con_sat_perc[t_ind].append(h_bestSol['CON_sat_%'])
                                    history_con_hard_sat_perc[t_ind].append(h_bestSol['CON_sat_%_hard'])
                                    history_con_soft_sat_perc[t_ind].append(h_bestSol['CON_sat_%_soft'])
                                    
                                    history_failures[t_ind] += 1
                                    t_ind += 1
                                
                                tot = len(history_times)
                                for j in range(t_ind, tot):
                                    history_con_sat_perc[j].append(1)
                                    history_con_hard_sat_perc[j].append(1)
                                    history_con_soft_sat_perc[j].append(1)

                                # for x in range(len(history_con_hard_sat_perc)):
                                #     print(history_con_sat_perc[x], end=" ")
                                #     print(history_con_hard_sat_perc[x], end=" ")
                                #     print(history_con_soft_sat_perc[x])

                    gen_stats_id = f'{gen_base_path}{i}-0'

                    # accessing _genstats.json
                    all_num_cons.append(gen_stats_data[gen_stats_id]['num_cons'])
                    all_num_hard_cons.append(gen_stats_data[gen_stats_id]['num_hard_cons'])
                    all_num_soft_cons.append(gen_stats_data[gen_stats_id]['num_soft_cons'])
                    if approach != 'nsga':
                        all_num_removed_cons.append(len(gen_stats_data[gen_stats_id][f'deleted-{approach}']))
            
            if not found_at_least_one_measurement:
                continue

            # Success Analysis
            totals = {}
            totals['scenes'] = scenes_count
            totals['attempts'] = num_attempts
            totals['successes'] = num_successes
            p = -1 if num_attempts == 0 else num_successes / num_attempts
            totals['%_succ'] = p
            totals['median_time_of_success'] = -1 if not all_times else statistics.median(all_times)
            totals['max_time_of_success'] = -1 if not all_times else max(all_times)
            totals['median_time_of_failure_(timeout)'] = -1 if not fail_times else statistics.median(fail_times)
            current_data['TOTALS'] = totals

            # Constraint removal analysis
            cons = {}
            cons['avg_num'] = statistics.mean(all_num_cons)
            cons['avg_num_hard'] = statistics.mean(all_num_hard_cons)
            cons['avg_num_soft'] = statistics.mean(all_num_soft_cons)
            # approach-specific analysis
            if approach == 'nsga':
                current_data['CONSTRAINTS'] = cons
                solutions = {}
                s1_dict = {}
                s1_dict['CON_avg_%_sat'] = -1 if not nsga_s1_con_sat_perc else statistics.mean(nsga_s1_con_sat_perc)
                s1_dict['CON_avg_%_sat_hard'] = -1 if not nsga_s1_con_hard_sat_perc else statistics.mean(nsga_s1_con_hard_sat_perc)
                s1_dict['CON_avg_%_sat_soft'] = -1 if not nsga_s1_con_soft_sat_perc else statistics.mean(nsga_s1_con_soft_sat_perc)

                s2_dict = {}
                s2_dict['CON_avg_%_sat'] = -1 if not nsga_s2_con_sat_perc else statistics.mean(nsga_s2_con_sat_perc)
                s2_dict['CON_avg_%_sat_hard'] = -1 if not nsga_s2_con_hard_sat_perc else statistics.mean(nsga_s2_con_hard_sat_perc)
                s2_dict['CON_avg_%_sat_soft'] = -1 if not nsga_s2_con_soft_sat_perc else statistics.mean(nsga_s2_con_soft_sat_perc)

                solutions['sol_best_global'] = s1_dict
                solutions['sol_best_Hard_Prio'] = s2_dict
                current_data['NSGA_SOLS'] = solutions

                # history
                if 'history' in r:
                    history = []
                    for x in range(len(history_times)):
                        h_sol_stats = {}
                        h_sol_stats['timeout'] = history_times[x]
                        history_succ_perc = (num_attempts - history_failures[x]) / num_attempts
                        h_sol_stats['%_succ'] = history_succ_perc
                        h_sol_stats['CON_avg_%_sat'] = statistics.mean(history_con_sat_perc[x])
                        h_sol_stats['CON_avg_%_sat_hard'] = statistics.mean(history_con_hard_sat_perc[x])
                        h_sol_stats['CON_avg_%_sat_soft'] = statistics.mean(history_con_soft_sat_perc[x])

                        history.append(h_sol_stats)

                    current_data['HISTORY'] = history
            else:
                # removal analysis
                cons['avg_num_soft_rm'] = 0 if not all_num_removed_cons else statistics.mean(all_num_removed_cons)
                cons['avg_%_soft_rm'] = cons['avg_num_soft_rm'] / cons['avg_num_soft']
                current_data['CONSTRAINTS'] = cons

                # rm sat analysis
                solution = {}
                solution['tot_succ_and_rm_sat'] = num_removed_succ
                p2 = -1 if num_attempts == 0 else num_removed_succ / num_attempts
                solution['%_succ_and_rm_sat'] = p2
                median2 = -1 if not all_removed_succ_percentages else statistics.median(all_removed_succ_percentages)
                solution['median_%_of_rm_sat'] = median2
                current_data['SCENIC-SOL'] = solution


            data[m][config][approach] = current_data

out_path = f'{out_dir}/results.json'
with open(out_path, 'w') as outfile:
    json.dump(data, outfile, indent=4)

print(f'Saved aggregate measurement stats at {out_path}')


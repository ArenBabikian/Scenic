import os
import json
from util import adjustSize, mk
import numpy as np
import matplotlib.pyplot as plt

# DATA CONFIG
maps = ['zalaFullcrop']
approaches = ['nsga']
configurations = ['2actors', '3actors', '4actors', '5actors', '6actors', '7actors']
num_scenes = range(10) #range(10)

# FIGURE CONFIG
default = plt.rcParams['axes.prop_cycle'].by_key()['color']
colors = ['#A50205', '#0876B5', '#CC6400', '#5813B7', default[4], default[5], default[6]]
opacity = 0.25

# SAVE CONFIG
out_dir = mk(f'docker/figures/Extra4')
src_dir = 'docker/results'

##########################
# FIGURE extra-4: Success Rate vs. Number of Constraints
##########################
def figExtra4():

    # DATA GATHERING
    data = {}
    for config in configurations:
        config_data = {}
        for approach in approaches:
            # only-considering aggregate-rm
            num_cons_2_succ_times = {}
            # agg_data = []
            # agg_rm_data = []
            for m in maps:

                for i in num_scenes:
                    if config in ['2actors', '3actors', '4actors']:
                        json_path = f'{src_dir}/RQ2/{m}/{config}/{i}-0/d-{approach}/nsga2-actors/_measurementstats.json'
                        nsga_path = f'{src_dir}/RQ2/{m}/{config}/{i}-0/d-nsga/nsga2-actors/_measurementstats.json'
                    else:
                        json_path = f'{src_dir}/RQ4/{m}/{config}/{i}-0/d-{approach}/nsga2-actors/_measurementstats.json'
                        nsga_path = f'{src_dir}/RQ4/{m}/{config}/{i}-0/d-nsga/nsga2-actors/_measurementstats.json'
                    if os.path.exists(json_path):
                        with open(json_path) as f:
                            json_data = json.load(f)
                        
                        json_res = json_data['results']
                        scene_num_attempts = len(json_res)
                        scene_num_successes = 0

                        # Get number of constraints
                        with open(nsga_path) as f:
                            nsga_data = json.load(f)
                            num_cons = nsga_data['results'][0]['CON_num']

                        scene_succ_times = []
                        # num_rm_successes = 0
                        # num_constraints = 0
                        for r in json_res:


                            # if not in map, add it to mapand add runtime

                            # else (if in map) add to corresponding map entry
                            if r['success']:
                                if approach == 'nsga' or (approach != 'nsga' and  r['CON_sat_%_rm'] == 1):
                                    scene_num_successes += 1
                                    scene_succ_times.append(r['time'])

                        if num_cons not in num_cons_2_succ_times:
                            num_cons_2_succ_times[num_cons] = {'num_att':scene_num_attempts,
                            'num_succ':scene_num_successes,
                            'succ_ts':scene_succ_times}
                        else:
                            num_cons_2_succ_times[num_cons]['num_att'] += scene_num_attempts
                            num_cons_2_succ_times[num_cons]['num_succ'] += scene_num_successes
                            num_cons_2_succ_times[num_cons]['succ_ts'].extend(scene_succ_times)

                        # succ_rate = 100*(-0.1 if num_attempts == 0 else num_successes / num_attempts)
                        # agg_data.append(succ_rate)

                        # succ_rm_rate = 100*(-0.1 if num_attempts == 0 else num_rm_successes / num_attempts)
                        # agg_rm_data.append(succ_rm_rate)

                # approach_data[m] = m_data

            # approach_data['aggregate'] = agg_data
            # if approach != 'nsga':
            #     approach_data['aggregate-rm'] = agg_rm_data
            # else:
            #     approach_data['aggregate-rm'] = agg_data
            config_data[approach] = num_cons_2_succ_times
        data[config] = config_data

    # FIGURE CREATION
    # import pprint 
    # pp = pprint.PrettyPrinter(indent=2)
    # pp.pprint(data)

    num_cols = 5
    n_groups = num_cols+1
    max_val = 100 + (100/num_cols)
    bar_width = 100/num_cols-1
    index = np.arange(0, max_val, max_val/n_groups)
    adjustSize()

    for config in configurations:

        # PLOT - w/o RM
        # fig2_helper(n_groups, data, config, max_val, bar_width, index, fig2_out_dir, '')
        # PLOT - w/ RM
        fig, ax = plt.subplots()
        cur_heights = [0 for _ in range(n_groups)]
        for i in range(len(approaches)):
            approach = approaches[i]
            # m = np.array(data[config][approach])
            m = data[config][approach]
            # print(m.tolist())

            data_cons = []
            data_att = []
            data_succ = []
            data_time = []

            ordered_list_of_cons = sorted(m.keys())
            for k in ordered_list_of_cons:
                data_cons.append(k)
                data_att.append(m[k]['num_att'])
                data_succ.append(m[k]['num_succ'])

            # if approach == 'sc1':
            plt.bar(data_cons, data_att, alpha=0.5)

            plt.plot(data_cons, data_succ, color=colors[i], label=f'{approach}')

            # hist_vals,_=np.histogram(vals,bins=np.linspace(0,max_val,n_groups+1))
            # # OPTION 1
            # # plt.bar(index, hist_vals, bar_width, color=colors[i], alpha=1 if approach == 'nsga' else opacity, bottom=cur_heights, label=f'{approach}{add}')
            # # cur_heights += hist_vals

            # # OPTION 2
            # sub_width = bar_width/4
            # pos = index+(i-1.5)*sub_width
            # # plt.bar(pos, hist_vals, sub_width, color=colors[i], alpha=1 if approach == 'nsga' or add == '-rm' else opacity, label=f'{approach}{add}')
            # plt.plot(pos, hist_vals, color=colors[i], alpha=1 if approach == 'nsga' or add == '-rm' else opacity, label=f'{approach}{add}')


        plt.xlabel(' Number of Constraints')
        plt.ylabel('Number of  Scenes')
        # # plt.title(f'{config}{add}')
        # if n_groups != 6:
        #     plt.xticks(index)
        # else:
        #     plt.xticks(index, ['0,10', '20,30', '40,50', '60,70', '80,90', '100'])

        # plt.legend()

        plt.tight_layout()
        # plt.show()
        save_path = f'{out_dir}/{config}.pdf'
        plt.savefig(save_path)

        print(f'Saved figure at {save_path}')

figExtra4()

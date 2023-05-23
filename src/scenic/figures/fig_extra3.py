import os
import json
from util import mk
import numpy as np
import matplotlib.pyplot as plt

# DATA CONFIG
maps = ['tram05', 'town02', 'zalaFullcrop']
configurations = ['2actors', '3actors', '4actors']
approach = 'nsga'
num_scenes = range(10) #range(10)

# FIGURE CONFIG
default = plt.rcParams['axes.prop_cycle'].by_key()['color']
colors = ['#A50205', '#0876B5', '#CC6400', '#5813B7', default[4], default[5], default[6]]

# SAVE CONFIG
out_dir = mk(f'docker/figures/Extra3')
src_dir = 'docker/results/RQ2'

##########################
# FIGURE extra-3: Graceful degradation of NSGA
##########################
def figExtra3():

    # DATA GATHERING
    data = {}
    agg_data = {}
    for config in configurations:
        agg_data[config] = []

    for m in maps:
        map_data = {}
        for config in configurations:
            app_data = []
            for i in num_scenes:                      
                json_path = f'{src_dir}/{m}/{config}/{i}-0/d-{approach}/nsga2-actors/_measurementstats.json'
                if os.path.exists(json_path):
                    with open(json_path) as f:
                        json_data = json.load(f)
                    
                    json_res = json_data['results']
                    for r in json_res:
                        if not r['success']:
                            # find % of sat 

                            sol = r['solutions']['sol_best_global']
                            perc_sat = (1-sol['CON_sat_%']) * 100

                            app_data.append(perc_sat)
                            agg_data[config].append(perc_sat)

            map_data[config] = app_data

        data[m] = map_data
    
    data['Aggregate'] = agg_data

    # FIGURE CREATION
    max_val = 110
    n_groups = 11
    index = np.arange(0, max_val, max_val/n_groups)
    bar_width = 10
    maps_and_agg = maps.copy()
    maps_and_agg.append('Aggregate')
    for m in maps_and_agg:

        fig, ax = plt.subplots()
        cur_heights = [0 for _ in range(n_groups)]
        for i in range(len(configurations)):
            config = configurations[i]
            vals = np.array(data[m][config])
            
            hist_vals,_=np.histogram(vals,bins=np.linspace(0,max_val,n_groups+1))
            # plt.scatter(index, hist_vals, label=approach)
            plt.bar(index+0.5*bar_width, hist_vals, bar_width, color=colors[i+4], edgecolor='k', bottom=cur_heights, label=config)
            
            cur_heights += hist_vals

        plt.xlabel('% of unsatisfied constraints')
        plt.ylabel('# Scenes')
        plt.title(f'{m}\nFor failed NSGA runs, what % of cons are not satisfied')
        plt.xticks(index)
        plt.legend()

        plt.tight_layout()
        # plt.show()
        save_path = f'{out_dir}/{m}.pdf'
        plt.savefig(save_path)

        print(f'Saved figure at {save_path}')

figExtra3()
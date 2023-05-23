import statistics
import os
import json
import seaborn as sns
import pandas as pd
from util import mk
import matplotlib.pyplot as plt

# DATA CONFIG
maps = ['tram05', 'town02', 'zalaFullcrop']
configurations = ['2actors', '3actors', '4actors']
num_scenes = range(10) #range(10)
approaches = ['sc1', 'sc3', 'sc2', 'nsga']

# FIGURE CONFIG
default = plt.rcParams['axes.prop_cycle'].by_key()['color']
colors = ['#A50205', '#0876B5', '#CC6400', '#5813B7', default[4], default[5], default[6]]

# SAVE CONFIG
src_dir = 'docker/results/RQ2'
gen_base_dir = 'measurements/data'
out_dir = mk(f'docker/figures/Extra2')

##########################
# FIGURE extra-2: Are rm-ed constraints being satisfied
##########################
def figExtra2():

    # DATA GATHERING
    data = {}
    for m in maps:
        fig3_data = {}

        for approach in approaches:
            if approach == 'nsga':
                continue
            perc_sat_rm_data = [] # 2D array
            num_rm_data = []
            for config in configurations:
                
                gen_stats_dir = f'{gen_base_dir}/{m}/{config}/'
                gen_stats_path = f'{gen_stats_dir}/_genstats.json'
                with open(gen_stats_path) as f:
                    gen_stats_data = json.load(f)
                
                num_rm_cons = [] # gnna find the median # TODO LATER
                perc_sat_rm = [] # will be shown in the stripplot

                for i in num_scenes:
                    json_path = f'{src_dir}/{m}/{config}/{i}-0/d-{approach}/_measurementstats.json'
                    if os.path.exists(json_path):

                        # get number of removed constraints
                        gen_stats_id = f'{gen_stats_dir}{i}-0'
                        rmed_cons = gen_stats_data[gen_stats_id][f'deleted-{approach}']
                        num_rm_cons.append(len(rmed_cons))

                        # get rm sat percentage
                        with open(json_path) as f:
                            json_data = json.load(f)
                        for r in json_data['results']:
                            if r['success']:
                                perc_sat = r['CON_sat_%_rm']
                                if perc_sat != -1:
                                    perc_sat_rm.append(perc_sat * 100)

                perc_sat_rm_data.append(perc_sat_rm)
                if len(perc_sat_rm) == 0:
                    mean = 'NA'
                    median = 'NA'
                else:
                    mean = statistics.mean(perc_sat_rm)
                    median = statistics.median(perc_sat_rm)
                print(f'{m}|{approach}|{config} = [mean={mean}, median={median}]')

                num_rm_data.append(num_rm_cons)

            fig3_data[approach] = {'numrm':num_rm_data, 'percsat':perc_sat_rm_data}

        data[m] = fig3_data

    # FIGURE CREATION
    split = 0.25
    for m in maps:
        fig, ax = plt.subplots()
        df_data = pd.DataFrame(columns=['approach', 'config', 'perc'])
        for i_a in range(len(approaches)):
            approach = approaches[i_a]
            if approach == 'nsga':
                continue            
            vals = data[m][approach]['percsat']
            for i_c in range(len(vals)):
                c_vals = vals[i_c]
                config = configurations[i_c]
                for v in c_vals:
                    df_data = df_data.append({'approach': approach, 'config': config, 'perc': v}, ignore_index=True)

            
                vals_rm = data[m][approach]['numrm'][i_c]
                median_rm = round(statistics.mean(vals_rm))
                ax.text(0.25+i_c-2*split+i_a*split, -12.5, str(median_rm), ha='center', va='center', size='large', bbox=dict(ec='k', fc='w'))

        df_counts = df_data.groupby(['approach', 'config', 'perc']).size().astype(float).reset_index(name='counts')
        
        sns.set_palette(sns.color_palette(colors[:]))
        sns.stripplot(x=df_counts.config, y=df_counts.perc, hue=df_counts.approach, sizes=df_counts.counts*10, dodge=True, jitter=0)

        plt.xlabel('Configurations')
        plt.ylabel(f'% of rm-ed constraints that are satisfied')
        ax.set_ylim(bottom=-20)
        plt.title(f'{m} - \nAmong successes, what % of rm-ed constraints are satisfied?')
        plt.legend()

        plt.tight_layout()
        # plt.show()
        save_path = f'{out_dir}/{m}.pdf'
        plt.savefig(save_path)

        print(f'Saved figure at {save_path}')

figExtra2() # also prints some statistcs
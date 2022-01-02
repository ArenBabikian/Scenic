
from copy import Error
import statistics
import os
import json
from pathlib import Path
import seaborn as sns
import pandas as pd


import numpy as np
import matplotlib.pyplot as plt

maps = ['tram05', 'town02', 'zalafullcrop']
configurations = ['2actors', '3actors', '4actors']
num_scenes = range(0, 20) #range(20)
approaches = ['nsga', 'sc1', 'sc2', 'sc3']

history_times = [30, 60, 120, 180, 300, 600, 1200, 1800, 2400, 3000]
tolerance = 1

colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
opacity = 0.5

data_dir = 'measurements/data'
src_dir = 'measurements/results'
out_dir = f'{src_dir}/aggregate'
Path(f'{out_dir}/').mkdir(parents=True, exist_ok=True)

##########################
# FIGURE 1: Success Rate Comparison
##########################
def figure1():
    fig1_out_dir = f'{out_dir}/fig1'
    Path(f'{fig1_out_dir}/').mkdir(parents=True, exist_ok=True)

    data = {}
    for m in maps:
        fig1_data = {}

        for approach in approaches:
            sr_data = []
            sr_rm_data = []
            num_at_data = []
            for config in configurations:
                num_attempts = 0
                num_successes = 0
                num_rm_successes = 0

                for i in num_scenes:
                    json_path = f'{src_dir}/{m}/{config}/{i}-0/d-{approach}/_measurementstats.json'
                    if os.path.exists(json_path):
                        with open(json_path) as f:
                            json_data = json.load(f)
                        
                        json_res = json_data['results']
                        num_attempts += len(json_res)

                        for r in json_res:
                            if r['success']:
                                num_successes += 1
                                if approach != 'nsga' and  r['CON_sat_%_rm'] == 1:
                                    num_rm_successes += 1

                succ_rate = 100*(-0.1 if num_attempts == 0 else num_successes / num_attempts)
                sr_data.append(succ_rate)
                succ_rm_rate = 100*(-0.1 if num_attempts == 0 else num_rm_successes / num_attempts)
                sr_rm_data.append(succ_rm_rate)
                num_at_data.append(num_attempts)

            fig1_data[approach] = {'sr':sr_data, 'at':num_at_data, 'srrm':sr_rm_data}

        data[m] = fig1_data

    #create figs
    for m in maps:

        n_groups = len(configurations)
        fig, ax = plt.subplots()
        index = np.arange(n_groups)
        bar_width = 0.2

        for i in range(len(approaches)):
            approach = approaches[i]
            pos = index+i*bar_width

            vals = data[m][approach]['sr']
            plt.bar(pos, vals, bar_width, color=colors[i], alpha=1 if approach == 'nsga' else opacity, label=approach)

            # #print number of attempts
            # attempts = data[m][approach]['at']
            # for i, v in enumerate(attempts):
            #     ax.text(pos[i], max(0, vals[i])+1, str(v), ha='center', fontweight='bold')
            
            # print success ratio
            for j, v in enumerate(vals):
                ax.text(pos[j], max(0, vals[j])+1, str(round(v)), ha='center', fontweight='bold')

            # PRINT w/ RM SAT
            if approach != 'nsga':
                vals_rm = data[m][approach]['srrm']
                plt.bar(pos, vals_rm, bar_width, color=colors[i], alpha=1, label=f'{approach}-rm')
                
                # print success ratio
                for i, v in enumerate(vals_rm):
                    ax.text(pos[i], max(0, vals_rm[i])+1, str(round(v)), ha='center', fontweight='bold')

        plt.xlabel('Configurations')
        plt.ylabel('Success rates')
        plt.title(m)
        plt.xticks(index + 1.5*bar_width, ('2 actors', '3 actors', '4 actors'))
        plt.legend()

        plt.tight_layout()
        # plt.show()
        save_path = f'{fig1_out_dir}/{m}.png'
        plt.savefig(save_path)

        print(f'Saved figure at {save_path}')


##########################
# FIGURE 2: Success Rate Distribution
##########################
def figure2():

    fig2_out_dir = f'{out_dir}/fig2'
    Path(f'{fig2_out_dir}/').mkdir(parents=True, exist_ok=True)

    data = {}
    for config in configurations:
        fig2_data = {}
        for approach in approaches:
            approach_data = {}
            agg_data = []
            agg_rm_data = []
            for m in maps:
                m_data = []
                num_attempts = 0
                num_successes = 0
                num_rm_successes = 0

                for i in num_scenes:
                    json_path = f'{src_dir}/{m}/{config}/{i}-0/d-{approach}/_measurementstats.json'
                    if os.path.exists(json_path):
                        with open(json_path) as f:
                            json_data = json.load(f)
                        
                        json_res = json_data['results']
                        num_attempts += len(json_res)

                        for r in json_res:
                            if r['success']:
                                num_successes += 1
                                if approach != 'nsga' and  r['CON_sat_%_rm'] == 1:
                                    num_rm_successes += 1

                    succ_rate = 100*(-0.1 if num_attempts == 0 else num_successes / num_attempts)
                    m_data.append(succ_rate)
                    agg_data.append(succ_rate)

                    succ_rm_rate = 100*(-0.1 if num_attempts == 0 else num_rm_successes / num_attempts)
                    agg_rm_data.append(succ_rm_rate)

                # approach_data[m] = m_data

            approach_data['aggregate'] = agg_data
            if approach != 'nsga':
                approach_data['aggregate-rm'] = agg_rm_data
            else:
                approach_data['aggregate-rm'] = agg_data


            fig2_data[approach] = approach_data

        data[config] = fig2_data


    #create figs
    max_val = 105
    n_groups = 21
    index = np.arange(0, max_val, max_val/n_groups)
    bar_width = 4
    for config in configurations:

        # PLOT - w/o RM
        fig, ax = plt.subplots()
        # ax.set_yscale('log')
        cur_heights = [0 for _ in range(n_groups)]
        for i in range(len(approaches)):
            approach = approaches[i]
            vals = np.array(data[config][approach]['aggregate'])
            
            hist_vals,_=np.histogram(vals,bins=np.linspace(0,max_val,n_groups+1))
            # plt.scatter(index, hist_vals, label=approach)
            plt.bar(index, hist_vals, bar_width, color=colors[i], alpha=1 if approach == 'nsga' else opacity, bottom=cur_heights, label=approach)
            cur_heights += hist_vals

        plt.xlabel('Success rate')
        plt.ylabel('# Scenes')
        plt.title(config)
        plt.xticks(index)
        plt.legend()

        plt.tight_layout()
        # plt.show()
        save_path = f'{fig2_out_dir}/{config}.png'
        plt.savefig(save_path)

        print(f'Saved figure at {save_path}')

        # PLOT - RM
        fig, ax = plt.subplots()
        cur_heights = [0 for _ in range(n_groups)]
        for i in range(len(approaches)):
            approach = approaches[i]
            vals_rm = np.array(data[config][approach]['aggregate-rm'])
            
            hist_vals_rm,_=np.histogram(vals_rm,bins=np.linspace(0,max_val,n_groups+1))
            # plt.scatter(index, hist_vals, label=approach)
            plt.bar(index, hist_vals_rm, bar_width, color=colors[i], alpha=1, bottom=cur_heights, label=f'{approach}-rm')
            cur_heights+=hist_vals_rm

        plt.xlabel('Success rate')
        plt.ylabel('# Scenes')
        plt.title(f'{config}-rm')
        plt.xticks(index)
        plt.legend()

        plt.tight_layout()
        # plt.show()
        save_path = f'{fig2_out_dir}/{config}-rm.png'
        plt.savefig(save_path)

        print(f'Saved figure at {save_path}')


##########################
# FIGURE 3: Are rm-ed constraints being satisfied
##########################
def figure3():
    fig3_out_dir = f'{out_dir}/fig3'
    Path(f'{fig3_out_dir}/').mkdir(parents=True, exist_ok=True)

    data = {}
    for m in maps:
        fig3_data = {}

        for approach in approaches:
            if approach == 'nsga':
                continue
            perc_sat_rm_data = [] # 2D array
            num_rm_data = []
            for config in configurations:
                
                gen_base_path = f'{data_dir}/{m}/{config}/'
                gen_stats_path = gen_base_path+'_genstats.json'
                with open(gen_stats_path) as f:
                    gen_stats_data = json.load(f)
                
                num_rm_cons = [] # gnna find the median # LATER 2
                perc_sat_rm = [] # will be shown in the stripplot

                for i in num_scenes:
                    json_path = f'{src_dir}/{m}/{config}/{i}-0/d-{approach}/_measurementstats.json'
                    if os.path.exists(json_path):

                        # get number of removed constraints
                        gen_stats_id = f'{gen_base_path}{i}-0'
                        rmed_cons = gen_stats_data[gen_stats_id][f'deleted-{approach}']
                        num_rm_cons.append(len(rmed_cons))
                        print

                        # get rm sat percentage
                        with open(json_path) as f:
                            json_data = json.load(f)
                        for r in json_data['results']:
                            if r['success']:
                                perc_sat = r['CON_sat_%_rm']
                                # if config == '2actors':
                                #     print(perc_sat)
                                if perc_sat != -1:
                                    perc_sat_rm.append(perc_sat * 100)

                perc_sat_rm_data.append(perc_sat_rm)
                num_rm_data.append(num_rm_cons)

            fig3_data[approach] = {'numrm':num_rm_data, 'percsat':perc_sat_rm_data}

        data[m] = fig3_data

    #create figs
    for m in maps:
        fig, ax = plt.subplots()
        df_data = pd.DataFrame(columns=['approach', 'config', 'perc'])
        for i in range(len(approaches)):
            approach = approaches[i]
            if approach == 'nsga':
                continue

            # vals = data[m][approach]['percsat']
            # medians = [statistics.mean(x) for x in vals]
            # print(medians)
            # print(pos)
            # plt.bar(pos, medians, bar_width, alpha=opacity, label=approach)
            
            vals = data[m][approach]['percsat'] # TODO currently only for ac2
            for i_c in range(len(vals)):
                c_vals = vals[i_c]
                config = configurations[i_c]
                for v in c_vals:
                    df_data = df_data.append({'approach': approach, 'config': config, 'perc': v}, ignore_index=True)

            # attempts = data[m][approach]['at']
            # for i, v in enumerate(attempts):
            #     ax.text(pos[i], max(0, vals[i])+1, str(v), ha='center', fontweight='bold')

        df_counts = df_data.groupby(['approach', 'config', 'perc']).size().astype(float).reset_index(name='counts')
        
        sns.set_palette(sns.color_palette(colors[1:]))
        sns.stripplot(x=df_counts.config, y=df_counts.perc, hue=df_counts.approach, sizes=df_counts.counts*10, dodge=True, jitter=0)

        plt.xlabel('Configurations')
        plt.ylabel(f'% of rm-ed constraints that are satisfied')
        plt.title(f'{m} - \nAmong successes, what % of rm-ed constraints are satisfied?')
        plt.legend()

        plt.tight_layout()
        # plt.show()
        save_path = f'{fig3_out_dir}/{m}.png'
        plt.savefig(save_path)

        print(f'Saved figure at {save_path}')


##########################
# FIGURE 4: Graceful degradation of NSGA
##########################
def figure4():

    fig4_out_dir = f'{out_dir}/fig4'
    Path(f'{fig4_out_dir}/').mkdir(parents=True, exist_ok=True)

    approach = 'nsga'
    data = {}
    agg_data = {}
    for config in configurations:
        agg_data[config] = []

    for m in maps:
        map_data = {}
        for config in configurations:
            app_data = []
            for i in num_scenes:
                json_path = f'{src_dir}/{m}/{config}/{i}-0/d-{approach}/_measurementstats.json'
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

    # import pprint 
    # pp = pprint.PrettyPrinter(indent=2)
    # pp.pprint(data)

    #create figs
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
        save_path = f'{fig4_out_dir}/{m}.png'
        plt.savefig(save_path)

        print(f'Saved figure at {save_path}')



# figure1()
# figure2()
# figure3()
figure4()

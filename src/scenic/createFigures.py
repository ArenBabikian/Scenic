
import statistics
import os
import json
from pathlib import Path
import seaborn as sns
import pandas as pd

import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import fisher_exact
from scipy.stats import ranksums
from pingouin import mwu


maps = ['tram05', 'town02', 'zalaFullcrop']
configurations = ['2actors', '3actors', '4actors']

num_scenes = range(10) #range(10)
approaches = ['sc1', 'sc3', 'sc2', 'nsga']
names_app = ['SceDef', 'SceReg', 'SceHyb', 'MOO']

history_times = [30, 60, 120, 180, 300, 600, 1200, 1800, 2400, 3000]
tolerance = 1

default = plt.rcParams['axes.prop_cycle'].by_key()['color']
colors = ['#A50205', '#0876B5', '#CC6400', '#5813B7', default[4], default[5], default[6]]
colors_light = ['#E8BFC0', '#C1DDEC', '#F2D8BF']
opacity = 0.25

base_dir = 'meas-off'
data_dir = f'{base_dir}/data'
src_dir = f'{base_dir}/results'
out_dir = f'{base_dir}/aggregate-temp'
Path(f'{out_dir}/').mkdir(parents=True, exist_ok=True)


def adjustSize(ax=plt, s=14):
    # ax.tick_params(axis='both', labelsize=MED_SIZE)
    
    ax.rc('font', size=s)         
    ax.rc('axes', titlesize=s)    
    ax.rc('axes', labelsize=s)
    ax.rc('xtick', labelsize=s)
    ax.rc('ytick', labelsize=s)
    ax.rc('legend', fontsize=s)
    ax.rc('figure', titlesize=s)


##########################
# FIGURE RQ1.1: Success Rate Comparison
##########################
def figRQ11(stat_sig=True, noPartial=False):
    if noPartial:
        fig1_out_dir = f'{out_dir}/RQ1.1'
    else:
        fig1_out_dir = f'{out_dir}/extra-1'
    Path(f'{fig1_out_dir}/').mkdir(parents=True, exist_ok=True)

    data = {}
    for m in maps:
        fig1_data = {}

        for approach in approaches:
            ns_data = []
            sr_data = []
            ns_rm_data = []
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

                ns_data.append(num_successes)
                succ_rate = 100*(-0.1 if num_attempts == 0 else num_successes / num_attempts)
                sr_data.append(succ_rate)
                ns_rm_data.append(num_rm_successes)
                succ_rm_rate = 100*(-0.1 if num_attempts == 0 else num_rm_successes / num_attempts)
                sr_rm_data.append(succ_rm_rate)
                num_at_data.append(num_attempts)

            fig1_data[approach] = {'sr':sr_data, 'ns':ns_data, 'at':num_at_data, 'srrm':sr_rm_data, 'nsrm':ns_rm_data}

        data[m] = fig1_data

    # import pprint 
    # pp = pprint.PrettyPrinter(indent=2)
    # pp.pprint(data)

    #create figs
    adjustSize()
    for m in maps:

        n_groups = len(configurations)
        fig, ax = plt.subplots()
        index = np.arange(n_groups)
        bar_width = 0.2

        for i in range(len(approaches)):
            approach = approaches[i]
            name = names_app[i]
            pos = index+i*bar_width

            if not noPartial or (noPartial and approach == 'nsga'):
                vals = data[m][approach]['sr']
                plt.bar(pos, vals, bar_width, 
                    # color=colors[i], 
                    color=colors[i] if approach == 'nsga' else colors_light[i],
                    # alpha=1 if approach == 'nsga' else opacity, 
                    label=name if approach == 'nsga' else f'{name}-sub', 
                    edgecolor=colors[i], 
                    hatch='//')

            # #print number of attempts
            # attempts = data[m][approach]['at']
            # for i, v in enumerate(attempts):
            #     ax.text(pos[i], max(0, vals[i])+1, str(v), ha='center', fontweight='bold')
            
            # print success ratio
            # for j, v in enumerate(vals):
            #     ax.text(pos[j], max(0, vals[j])+1, str(round(v)), ha='center', fontweight='bold')

            # PRINT w/ RM SAT
            if approach != 'nsga':
                vals_rm = data[m][approach]['srrm']
                plt.bar(pos, vals_rm, bar_width, color=colors[i], alpha=1, label=name)
                
                # print success ratio
                # for i, v in enumerate(vals_rm):
                #     ax.text(pos[i], max(0, vals_rm[i])+1, str(round(v)), ha='center', fontweight='bold')

        plt.xlabel('Scene size')
        plt.ylabel('Success rate (%)')
        # plt.title(m)
        plt.xticks(index + 1.5*bar_width, ('2 actors', '3 actors', '4 actors'))
        # plt.legend()
        plt.tight_layout()
        # plt.show()
        save_path = f'{fig1_out_dir}/{m}.pdf'
        plt.savefig(save_path)

        print(f'Saved figure at {save_path}')

        if m == 'zalaFullcrop':
            # export Legend
            # legend = plt.legend(loc=3, framealpha=1, frameon=False)
            plt.axis('off')
            box = ax.get_position()
            ax.set_position([box.x0, box.y0 + box.height * 0.2,
                            box.width, box.height * 0.9])

            # Put a legend below current axis
            legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), framealpha=1, frameon=False, ncol=7)

            # legend = plt.legend(ncol=7, framealpha=1, frameon=False)
            fig  = legend.figure
            fig.canvas.draw()
            bbox  = legend.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
            legend_path = f'{fig1_out_dir}/legend.pdf'
            fig.savefig(legend_path, dpi="figure", bbox_inches=bbox)
            # fig.savefig(legend_path)
            print(f'Saved figure at {legend_path}')


        if stat_sig:
            print(">>>Statistical Significance<<<")
            thresh=0.05
            print(f'Map: {m}')
            for i_c in range(len(configurations)):
                config = configurations[i_c]
                print(f'  Config: {config}')
                print('  Details:')
                for approach in approaches:
                    at = data[m][approach]['at'][i_c]
                    ns = data[m][approach]['ns'][i_c]
                    nsrm = data[m][approach]['nsrm'][i_c]
                    print(f'    {approach}(at={at}, ns={ns}, ns-rm={nsrm})')

                print('    Results:')
                nsga_at = data[m]['nsga']['at'][i_c]
                nsga_ns = data[m]['nsga']['ns'][i_c]
                for approach in approaches[:-1]:
                    at = data[m][approach]['at'][i_c]
                    ns = data[m][approach]['ns'][i_c]
                    nsrm = data[m][approach]['nsrm'][i_c]

                    # _, pvalue = fisher_exact([[nsga_at, nsga_ns],[at, ns]])
                    # # if pvalue > thresh:
                    # #     Fore.RED
                    # print(('~~~~' if pvalue>thresh else '    ') + f'nsga*{approach}: (pvalue={pvalue})')
                    
                    # print(f'nsga: {nsga_at}/{nsga_ns} | {approach}: {at}/{nsrm}')
                    # print([[at-nsrm, nsrm],[nsga_at-nsga_ns, nsga_ns]])
                    oddsratio, pvaluerm = fisher_exact([[nsga_ns, nsga_at-nsga_ns],[nsrm, at-nsrm]])
                    print(('~~~~' if pvaluerm>thresh else '    ') + f'nsga*{approach}-rm: (pvalue={pvaluerm}) (oddsrat={oddsratio})')
            print(">>>End Statistical Significance<<<")


##########################
# FIGURE RQ1.2: Runtime Analysis
##########################
def figRQ12(stat_sig=False):
    fig5_out_dir = f'{out_dir}/RQ1.2'
    Path(f'{fig5_out_dir}/').mkdir(parents=True, exist_ok=True)

    data = {}
    for m in maps:
        fig5_data = {}
        for approach in approaches:
            rt_data = [] # 2D array
            su_data = []
            sr_data = [] #obs
            sr_rm_data = [] #obs
            num_at_data = [] #obs
            for config in configurations:
                rt_con_data = []
                num_attempts = 0 #obs
                num_successes = 0 #obs
                num_rm_successes = 0 #obs

                for i in num_scenes:
                    json_path = f'{src_dir}/{m}/{config}/{i}-0/d-{approach}/_measurementstats.json'
                    if os.path.exists(json_path):
                        with open(json_path) as f:
                            json_data = json.load(f)
                        
                        json_res = json_data['results']
                        num_attempts += len(json_res)

                        for r in json_res:
                            if r['success']:
                                # rt_con_data.append(r['time']) # TEMP RMed
                                num_successes += 1
                                if approach == 'nsga':
                                    rt_con_data.append(r['time'])
                                elif  r['CON_sat_%_rm'] == 1:
                                    num_rm_successes += 1
                                    rt_con_data.append(r['time'])

                rt_data.append(rt_con_data)
                su_data.append(num_successes)
                # OBS
                succ_rate = 100*(-0.1 if num_attempts == 0 else num_successes / num_attempts)
                sr_data.append(succ_rate)
                succ_rm_rate = 100*(-0.1 if num_attempts == 0 else num_rm_successes / num_attempts)
                sr_rm_data.append(succ_rm_rate)
                num_at_data.append(num_attempts)

            fig5_data[approach] = {'rt': rt_data, 'su':su_data, 'sr':sr_data, 'at':num_at_data, 'srrm':sr_rm_data}

        data[m] = fig5_data

    # import pprint 
    # pp = pprint.PrettyPrinter(indent=2)
    # pp.pprint(data)

    #create figs
    adjustSize()
    for m in maps:

        n_groups = len(configurations)
        fig, ax = plt.subplots()
        # ax.set_yscale('log')
        index = np.arange(n_groups)
        bar_width = 0.2

        bps = []

        for i in range(len(approaches)):
            approach = approaches[i]
            pos = index+i*bar_width

            vals = data[m][approach]['rt']
            if len(vals[2]) == 0:
                median = 'NA'
            else:
                median = statistics.median(vals[2])
            # print(f'{m}|{approach} = [median={median}]')
            # means = [statistics.mean(x) for x in vals]
            # plt.bar(pos, means, bar_width, color=colors[i], alpha=1 if approach == 'nsga' else opacity, label=approach)
            bps.append(plt.boxplot(vals, positions=pos, widths=bar_width,
                patch_artist=True,
                boxprops=dict(facecolor=colors[i],color='k'),
                capprops=dict(color='k'),
                whiskerprops=dict(color=colors[i]),
                flierprops=dict(color=colors[i], markeredgecolor=colors[i]),
                medianprops=dict(color='k'),
                labels=[approach, approach, approach]))

            # # vals = data[m][approach]['rt']
            # medians = [statistics.median(x) for x in vals]
            # plt.scatter(pos, medians, color='k', alpha=1 if approach == 'nsga' else opacity, label=approach)

            # # #print number of successes
            # attempts = data[m][approach]['at']
            # successes = data[m][approach]['su']
            # for j, v in enumerate(successes):
            #     ax.text(pos[j], means[j]+math.log(2), str(v), ha='center', fontweight='bold')

        plt.xlabel('Scene size')
        plt.ylabel('Runtime (s)')
        # plt.title(m)
        plt.xticks(index + 1.5*bar_width, ('2 actors', '3 actors', '4 actors'))
        # plt.legend([bp['boxes'][0] for bp in bps], approaches)

        plt.tight_layout()
        # plt.show()
        save_path = f'{fig5_out_dir}/{m}.pdf'
        plt.savefig(save_path)

        print(f'Saved figure at {save_path}')

        if stat_sig:
            alt = "greater"
            # alt = 'two-sided'
            incl_nf = True
            incl_np = False
            incl_paf = False
            print(">>>Statistical Significance<<<")
            print('nf=no failure times, np=no partial failure times, paf=partial as failure ')
            print(alt)
            thresh=0.05
            print(f'Map: {m}')
            for i_c in range(len(configurations)):
                config = configurations[i_c]
                if config == "4actors" or  config == "2actors"  :
                    continue
                print(f'  Config: {config}')
                # print('  Details:')
                # for approach in approaches:
                #     at = data[m][approach]['at'][i_c]
                #     ns = data[m][approach]['ns'][i_c]
                #     nsrm = data[m][approach]['nsrm'][i_c]
                #     print(f'    {approach}(at={at}, ns={ns}, ns-rm={nsrm})')

                print('  Results:')
                num_att = data[m]['nsga']['at'][i_c]
                num_suc = data[m]['nsga']['su'][i_c]
                nsga_times = data[m]['nsga']['rt'][i_c]

                nsga_times_w_fail = nsga_times + [600 for _ in range((num_att-num_suc))]
                assert len(nsga_times) == num_suc
                assert len(nsga_times_w_fail) == num_att

                for approach in approaches[:-1]:

                    app_att = data[m][approach]['at'][i_c]
                    assert app_att == 100
                    app_suc = data[m][approach]['su'][i_c]
                    app_suc_w_rm = int(data[m][approach]['srrm'][i_c])
                    assert app_suc_w_rm <= app_suc

                    # NO FAILURE
                    if incl_nf:
                        app_times = data[m][approach]['rt'][i_c]
                        a12 = get_a12(nsga_times, app_times)
                        if len(app_times) == 0:
                            print(f'    nf  = (EMPTY)')
                        else:
                            # if config=='3actors' and approach=='sc1':
                            print(len(nsga_times))
                            print(statistics.median(app_times))
                            df = mwu(nsga_times, app_times, alternative=alt)
                            p=df["p-val"]["MWU"]
                            # print(df)
                            print(('~~~~' if p>thresh else '    ') + f'nf  = nsga*{approach}: (pvalue={p}) (u1={df["U-val"]["MWU"]}) (eff={df["CLES"]["MWU"]})')


                            # factors = [15,16,17,18,19,20,21,22,23,24,25] # 2actors
                            factors = [291, 292, 293, 294, 295]
                            factors= [321, 322, 323, 324, 325]
                            # factors = [2,3,4,5,6] # 3actors
                            for factor in factors:
                                dffac = mwu(nsga_times, [factor*i for i in app_times], alternative=alt)
                                pfac=dffac["p-val"]["MWU"]
                                print(('~~~~' if pfac>thresh else '    ') + f'      fact={factor}: (pvalue={pfac}) (u1={dffac["U-val"]["MWU"]}) (eff={dffac["CLES"]["MWU"]})')

                    # ONLY COMPLETE FAILURES AS TIMEOUT
                    if incl_np:
                        app_times_w_fail = app_times + [600 for _ in range((app_att-app_suc))]
                        a12 = get_a12(nsga_times_w_fail, app_times_w_fail)
                        df = mwu(nsga_times_w_fail, app_times_w_fail, alternative=alt)
                        p=df["p-val"]["MWU"]
                        print(('~~~~' if p>thresh else '    ') + f'np  = nsga*{approach}: (pvalue={p}) (u1={df["U-val"]["MWU"]}) (eff={df["CLES"]["MWU"]})')

                    # EVEN PARTIAL FAILURES AS TIMEOUT
                    if incl_paf:
                        if approach != 'nsga':
                            app_times_part_as_fail = app_times + [600 for _ in range((app_att-app_suc_w_rm))]
                        else:
                            app_times_part_as_fail = app_times_w_fail
                        assert len(app_times_part_as_fail) == 100
                        a12 = get_a12(nsga_times_w_fail, app_times_part_as_fail)
                        df = mwu(nsga_times_w_fail, app_times_part_as_fail, alternative=alt)
                        p=df["p-val"]["MWU"]
                        print(('~~~~' if p>thresh else '    ') + f'paf  = nsga*{approach}: (pvalue={p}) (u1={df["U-val"]["MWU"]}) (eff={df["CLES"]["MWU"]})')

            print(">>>End Statistical Significance<<<")

def get_a12(a, b):
    rs_m = len(a)
    rs_n = len(b)
    out = ranksums(a, b)
    # print(out)
    ranksum=out[0]
    return (ranksum/rs_m - ((rs_m+1)/2))/rs_n


##########################
# FIGURE RQ1.3: Success Rate Distribution
##########################
def figRQ13():

    fig2_out_dir = f'{out_dir}/RQ1.3'
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

                for i in num_scenes:
                    json_path = f'{src_dir}/{m}/{config}/{i}-0/d-{approach}/_measurementstats.json'
                    if os.path.exists(json_path):
                        with open(json_path) as f:
                            json_data = json.load(f)
                        
                        json_res = json_data['results']
                        num_attempts = len(json_res)

                        num_successes = 0
                        num_rm_successes = 0
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

    
    import pprint 
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(data)


    #create figs
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
        fig2_helper(n_groups, data, config, max_val, bar_width, index, fig2_out_dir, '-rm')

##########################
# FIGURE RQ1.4: 
##########################
def figRQ14():
    # Set up output file
    figRQ14_out_dir = f'{out_dir}/RQ1.4'
    Path(f'{figRQ14_out_dir}/').mkdir(parents=True, exist_ok=True)

    m = 'town02'    # map name
    cons_types = ['CANSEE', 'HASINFRONT', 'HASBEHIND', 'DISTCLOSE', 'HASTOLEFT', 'DISTMED', 'HASTORIGHT', 'DISTFAR']

    # Extract data (pb map values)
    data = {}
    map_val_data = [] # 2D array, pb map vals for each scene
    num_attempts = 0 
    num_successes = 0 
    num_rm_successes = 0 

    # Measurements for run of single abstract spec
    json_path = '../../examples/basic/_output/_measurementstats.json'
    if os.path.exists(json_path):
        with open(json_path) as f:
            json_data = json.load(f)
        
        json_res = json_data['results']
        num_attempts += len(json_res)
        
        # Loop through each concrete scene
        for r in json_res:
            if r['success']:
                num_successes += 1
                sols = r['solutions']
                last_sol_key = list(sols)[-1]
                last_sol = sols[last_sol_key]
                # only add data if all constraints are fully satisfied
                if last_sol['CON_sat_%'] == 1.0: 
                    map_val_data.append(list(last_sol['PB_Map_vals'].values()))
    else:
        print("json_path does not exist")

    map_vals_per_cons = np.array(map_val_data).T.tolist()
    succ_rate = 100*(-0.1 if num_attempts == 0 else num_successes / num_attempts)
    succ_rm_rate = 100*(-0.1 if num_attempts == 0 else num_rm_successes / num_attempts)

    data = {'vals': map_vals_per_cons, 'su':num_successes, 'sr':succ_rate, 'at':num_attempts, 'srrm':succ_rm_rate}

    # import pprint 
    # pp = pprint.PrettyPrinter(indent=2)
    # pp.pprint(data)

    #create figs
    adjustSize()
    fig, ax = plt.subplots()
    plt.figure(figsize=(12, 5))
    n_cons_types = len(cons_types)
    bar_width = 0.2
    index = np.arange(n_cons_types)*10
    pos = index+bar_width
    vals = data['vals']

    bps = []
    bps.append(plt.boxplot(vals, positions=pos, widths=bar_width,
        patch_artist=True,
        boxprops=dict(facecolor=colors[0],color='k'),
        capprops=dict(color='k'),
        whiskerprops=dict(color=colors[0]),
        flierprops=dict(color=colors[0], markeredgecolor=colors[0]),
        medianprops=dict(color='k')))

    plt.xlabel('Constraint Type')
    plt.ylabel('Heuristic')
    # plt.title(m)
    plt.xticks(index + 1.5*bar_width, ('CANSEE', 'HASINFRONT', 'HASBEHIND', 'DISTCLOSE', 'HASTOLEFT', 'DISTMED', 'HASTORIGHT', 'DISTFAR'))
    # plt.legend([bp['boxes'][0] for bp in bps], approaches)

    plt.tight_layout()
    # plt.show()
    save_path = f'{figRQ14_out_dir}/plot.pdf'
    plt.savefig(save_path)

    print(f'Saved figure at {save_path}')

def get_a12(a, b):
    rs_m = len(a)
    rs_n = len(b)
    out = ranksums(a, b)
    # print(out)
    ranksum=out[0]
    return (ranksum/rs_m - ((rs_m+1)/2))/rs_n

def fig2_helper(n_groups, data, config, max_val, bar_width, index, fig2_out_dir, add):
    fig, ax = plt.subplots()
    cur_heights = [0 for _ in range(n_groups)]
    for i in range(len(approaches)):
        approach = approaches[i]
        vals = np.array(data[config][approach][f'aggregate{add}'])
        
        hist_vals,_=np.histogram(vals,bins=np.linspace(0,max_val,n_groups+1))
        # OPTION 1
        # plt.bar(index, hist_vals, bar_width, color=colors[i], alpha=1 if approach == 'nsga' else opacity, bottom=cur_heights, label=f'{approach}{add}')
        # cur_heights += hist_vals

        # OPTION 2
        sub_width = bar_width/4
        pos = index+(i-1.5)*sub_width
        plt.bar(pos, hist_vals, sub_width, color=colors[i], alpha=1 if approach == 'nsga' or add == '-rm' else opacity, label=f'{approach}{add}')


    plt.xlabel('Success rate (%)')
    plt.ylabel('Number of  Scenes')
    # plt.title(f'{config}{add}')
    if n_groups != 6:
        plt.xticks(index)
    else:
        plt.xticks(index, ['0,10', '20,30', '40,50', '60,70', '80,90', '100'])

    # plt.legend()

    plt.tight_layout()
    # plt.show()
    if add:
        save_path = f'{fig2_out_dir}/{config}.pdf'
    else:
        save_path = f'{fig2_out_dir}/obs-{config}.pdf'
    plt.savefig(save_path)

    print(f'Saved figure at {save_path}')


##########################
# FIGURE RQ2: Success Rate vs. Number of Constraints DATA
##########################
def figRQ2():

    fig8_out_dir = f'{out_dir}/RQ2'
    Path(f'{fig8_out_dir}/').mkdir(parents=True, exist_ok=True)

    
    m = 'zalaFullcrop'
    approach = 'nsga'
    configs = ['none', 'r', 'rc', 'rcv', 'rcvd', 'rcvdp']
    names = ['\u00F8', 'R', 'RC', 'RCV', 'RCVD', 'RCVDP']

    data = {}
    # for config in configurations:
    # config_data = {}
    # only-considering aggregate-rm
    num_cons_2_succ_times = {}
    # agg_data = []
    # agg_rm_data = []

    for j in range(len(configs)):
        c = configs[j]
        config_data = {'num_att':0, 'num_succ':0, 'times_succ':[], }

        for i in range(10):
            scene_data = {"id":i}
            # id, numcons, succ rate, median time
            json_path = f'{src_dir}/{m}/constraints/{c}/{i}/_measurementstats.json'

            if os.path.exists(json_path):
                with open(json_path) as f:
                    json_data = json.load(f)
                
                json_res = json_data['results']
                config_data['num_att'] += len(json_res)
                scene_num_successes = 0


                scene_succ_times = []
                # num_rm_successes = 0
                # num_constraints = 0
                for r in json_res:

                    # if not in map, add it to mapand add runtime

                    # else (if in map) add to corresponding map entry
                    if r['success']:
                        config_data['num_succ'] += 1
                        config_data['times_succ'].append(r['time'])

            config_data["median_time"] = -1 if not config_data['times_succ'] else statistics.median(config_data['times_succ'])
        data[names[j]] = config_data

        # for i in num_scenes:
        #     scene_data = {"id":i}
        #     # id, numcons, succ rate, median time
        #     json_path = f'{src_dir}/{m}/{config}/{i}-0/d-{approach}/_measurementstats.json'

        #     if os.path.exists(json_path):
        #         with open(json_path) as f:
        #             json_data = json.load(f)
                
        #         json_res = json_data['results']
        #         scene_num_attempts = len(json_res)
        #         scene_num_successes = 0


        #         scene_succ_times = []
        #         # num_rm_successes = 0
        #         # num_constraints = 0
        #         for r in json_res:


        #             # if not in map, add it to mapand add runtime

        #             # else (if in map) add to corresponding map entry
        #             if r['success']:
        #                 if approach == 'nsga' or (approach != 'nsga' and  r['CON_sat_%_rm'] == 1):
        #                     scene_num_successes += 1
        #                     scene_succ_times.append(r['time'])

        #         scene_data["num_succ"] = scene_num_successes
        #         scene_data["times_succ"] = scene_succ_times
        #         scene_data["median_time"] = -1 if not scene_succ_times else statistics.median(scene_succ_times)

        # # data.append(scene_data)

    import pprint 
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(data)

    plot_data = {'nm':[], 'sr':[], 'rt':[]}
    for x in data:
        plot_data['nm'].append(x)
        plot_data['sr'].append(100* data[x]['num_succ'] / data[x]['num_att'])
        plot_data['rt'].append(data[x]['median_time'])

    pp.pprint(plot_data)
    #create figs
    ratio = 0.5
    def fix_ratio(axS, axT):
        x_left, x_right = axS.get_xlim()
        y_low, y_high = axS.get_ylim()
        axT.set_aspect(abs((x_right-x_left)/(y_low-y_high))*ratio)

    adjustSize(s=12)
    n_groups = len(configs)
    # _, ax1 = plt.subplot(adjustable='box')
    # ax1 = fig.add_subplot(111, adjustable='box')
    from mpl_toolkits.axes_grid1 import host_subplot
    ax1 = host_subplot(111, adjustable='box')
    index = np.arange(n_groups)
    bar_width = 0.4
    labels=['Success Rate (%)', 'Median Runtime (s)']

    
    

    color = '#2F9E00'
    ax1.set_ylabel(labels[0], color=color)
    # ax1.set_ylim(bottom=0)
    bar1 = ax1.bar(index, plot_data['sr'], bar_width, 
        label=labels[0], color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    
    ax2 = plt.twinx()
    # ax2.set_ylim(bottom=0)
    color = '#0020A2'
    ax2.set_ylabel(labels[1], color=color)
    # bar2 = ax2.bar(index+bar_width, [-1 if len(rt)==0 else statistics.median(rt) for rt in plot_data['rt']], bar_width,label=labels[1], color=color)
    
    bar2 = ax2.bar(index+bar_width, plot_data['rt'], bar_width, label=labels[1], color=color)
    ax2.tick_params(axis='y', labelcolor=color) 
    fix_ratio(ax1, ax1)
    fix_ratio(ax2, ax2)
    
    plt.xlabel('Included constraints')
    plt.xticks(index + 0.5*bar_width, tuple(names))
    plt.legend([bar1, bar2], labels, loc=9)

    # plt.tight_layout()
    # plt.show()
    save_path = f'{fig8_out_dir}/{m}.pdf'
    plt.savefig(save_path, bbox_inches='tight')

    print(f'Saved figure at {save_path}')
    
    exit()


##########################
# FIGURE RQ3: Scalability wrt. number of actors
##########################
def figRQ3():
    fig6_out_dir = f'{out_dir}/RQ3'
    Path(f'{fig6_out_dir}/').mkdir(parents=True, exist_ok=True)

    m = 'zalaFullcrop'
    approach = 'nsga'
    configurations = ['4actors', '5actors', '6actors', '7actors']

    data = {'rt':[], 'sr':[]}
    for config in configurations:
        rt_con_data = []
        num_attempts = 0 #obs
        num_successes = 0 #obs

        for i in num_scenes:
            json_path = f'{src_dir}/{m}/scale/{config}/{i}-0/d-{approach}/_measurementstats.json'
            if os.path.exists(json_path):
                with open(json_path) as f:
                    json_data = json.load(f)
                
                json_res = json_data['results']
                num_attempts += len(json_res)

                for r in json_res:
                    if r['success']:
                        # rt_con_data.append(r['time']) # TEMP RMed
                        num_successes += 1
                        rt_con_data.append(r['time'])

        succ_rate = 100*(-0.1 if num_attempts == 0 else num_successes / num_attempts)

        data['rt'].append(rt_con_data)
        data['sr'].append(succ_rate)


    #create figs
    ratio = 0.5
    def fix_ratio(axS, axT):
        x_left, x_right = axS.get_xlim()
        y_low, y_high = axS.get_ylim()
        axT.set_aspect(abs((x_right-x_left)/(y_low-y_high))*ratio)

    adjustSize(s=12)
    n_groups = len(configurations)
    # _, ax1 = plt.subplot(adjustable='box')
    # ax1 = fig.add_subplot(111, adjustable='box')
    from mpl_toolkits.axes_grid1 import host_subplot
    ax1 = host_subplot(111, adjustable='box')
    index = np.arange(n_groups)
    bar_width = 0.4
    labels=['Success Rate (%)', 'Median Runtime (s)']

    
    

    color = '#2F9E00'
    ax1.set_ylabel(labels[0], color=color)
    # ax1.set_ylim(bottom=0)
    bar1 = ax1.bar(index, data['sr'], bar_width, 
        label=labels[0], color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    
    ax2 = plt.twinx()
    # ax2.set_ylim(bottom=0)
    color = '#0020A2'
    ax2.set_ylabel(labels[1], color=color)
    bar2 = ax2.bar(index+bar_width, [-1 if len(rt)==0 else statistics.median(rt) for rt in data['rt']], bar_width,
    label=labels[1], color=color)
    ax2.tick_params(axis='y', labelcolor=color) 
    fix_ratio(ax1, ax1)
    fix_ratio(ax2, ax2)
    
    plt.xlabel('Scene size')
    plt.xticks(index + 0.5*bar_width, tuple(configurations))
    plt.legend([bar1, bar2], labels, loc=9)

    # plt.tight_layout()
    # plt.show()
    save_path = f'{fig6_out_dir}/{m}.pdf'
    plt.savefig(save_path, bbox_inches='tight')

    print(f'Saved figure at {save_path}')


##########################
# FIGURE extra-2: Are rm-ed constraints being satisfied
##########################
def figExtra2():
    fig3_out_dir = f'{out_dir}/extra-2'
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
                gen_base_path_key = f'measurements/data/{m}/{config}/' # TEMP
                gen_stats_path = gen_base_path+'_genstats.json'
                with open(gen_stats_path) as f:
                    gen_stats_data = json.load(f)
                
                num_rm_cons = [] # gnna find the median # TODO LATER
                perc_sat_rm = [] # will be shown in the stripplot

                for i in num_scenes:
                    json_path = f'{src_dir}/{m}/{config}/{i}-0/d-{approach}/_measurementstats.json'
                    if os.path.exists(json_path):

                        # get number of removed constraints
                        gen_stats_id = f'{gen_base_path_key}{i}-0'
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

    #create figs
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
                ax.text(i_c-2*split+i_a*split, -12.5, str(median_rm), ha='center', va='center', size='large', bbox=dict(ec='k', fc='w'))

        df_counts = df_data.groupby(['approach', 'config', 'perc']).size().astype(float).reset_index(name='counts')
        
        sns.set_palette(sns.color_palette(colors[1:]))
        sns.stripplot(x=df_counts.config, y=df_counts.perc, hue=df_counts.approach, sizes=df_counts.counts*10, dodge=True, jitter=0)

        plt.xlabel('Configurations')
        plt.ylabel(f'% of rm-ed constraints that are satisfied')
        ax.set_ylim(bottom=-20)
        plt.title(f'{m} - \nAmong successes, what % of rm-ed constraints are satisfied?')
        plt.legend()

        plt.tight_layout()
        # plt.show()
        save_path = f'{fig3_out_dir}/{m}.pdf'
        plt.savefig(save_path)

        print(f'Saved figure at {save_path}')


##########################
# FIGURE extra-3: Graceful degradation of NSGA
##########################
def figExtra3():

    fig4_out_dir = f'{out_dir}/extra-3'
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
        save_path = f'{fig4_out_dir}/{m}.pdf'
        plt.savefig(save_path)

        print(f'Saved figure at {save_path}')


##########################
# FIGURE extra-4: Success Rate vs. Number of Constraints
##########################
def figExtra4():

    fig7_out_dir = f'{out_dir}/extra-4'
    Path(f'{fig7_out_dir}/').mkdir(parents=True, exist_ok=True)

    maps = ['zalaFullcrop']
    approaches = ['nsga']
    configurations = ['2actors', '3actors', '4actors', '5actors', '6actors', '7actors']

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
                        json_path = f'{src_dir}/{m}/{config}/{i}-0/d-{approach}/_measurementstats.json'
                        nsga_path = f'{src_dir}/{m}/{config}/{i}-0/d-nsga/_measurementstats.json'
                    else:
                        json_path = f'{src_dir}/{m}/scale/{config}/{i}-0/d-{approach}/_measurementstats.json'
                        nsga_path = f'{src_dir}/{m}/scale/{config}/{i}-0/d-nsga/_measurementstats.json'
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

    
    import pprint 
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(data)


    #create figs
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
        save_path = f'{fig7_out_dir}/{config}.pdf'
        plt.savefig(save_path)

        print(f'Saved figure at {save_path}')


# figRQ11(True, False)
# figRQ12(True)
# figRQ13()
figRQ14()
# figRQ2()
# figRQ3()
# figExtra2() # also prints some statistcs
# figExtra3()
# figExtra4()

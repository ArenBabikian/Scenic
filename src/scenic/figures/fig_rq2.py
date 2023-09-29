import statistics
import os
import json
from pathlib import Path
from util import adjustSize, mk
import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import fisher_exact
from scipy.stats import ranksums
from pingouin import mwu

# DATA CONFIG
maps = ['tram05', 'town02', 'zalaFullcrop']
configurations = ['2actors', '3actors', '4actors']
num_scenes = range(10)
approaches = ['sc1', 'sc3', 'sc2', 'nsga']
names_app = ['SceDef', 'SceReg', 'SceHyb', 'MHS']

# FIGURE CONFIG
default = plt.rcParams['axes.prop_cycle'].by_key()['color']
colors = ['#A50205', '#0876B5', '#CC6400', '#5813B7', default[4], default[5], default[6]]
colors_light = ['#E8BFC0', '#C1DDEC', '#F2D8BF']
opacity = 0.25

# SAVE CONFIG
src_dir = 'docker/results/RQ2'
out_dir = mk(f'docker/figures/RQ2')
out_dir_extra = f'docker/figures/Extra1'

##########################
# FIGURE RQ2.1: Success Rate Comparison
##########################
def figRQ21(stat_sig=True, noPartial=True):
    if noPartial:
        fig1_out_dir = mk(f'{out_dir}/RQ2.1')
    else:
        fig1_out_dir = mk(out_dir_extra)

    # DATA GATHERING
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
                    if approach != 'nsga':
                        json_path = f'{src_dir}/{m}/{config}/{i}-0/d-{approach}/_measurementstats.json'
                    else:                        
                        json_path = f'{src_dir}/{m}/{config}/{i}-0/d-{approach}/nsga2-actors/_measurementstats.json'
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
    # FIGURE CREATION
    
    # import pprint 
    # pp = pprint.PrettyPrinter(indent=2)
    # pp.pprint(data)

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
        plt.ylim(0, 105)
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
            # fig.savefig(legend_path)s
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
# FIGURE RQ2.1.x: Success Rate Comparison with distribution
##########################
def figRQ21x():
    fig1_out_dir = mk(f'{out_dir}/RQ2.1.distribution')

    # DATA GATHERING
    data = {}
    for m in maps:
        fig1_data = {}

        for approach in approaches:
            ns_data = []
            sr_data = []
            srps_data = []
            ns_rm_data = []
            sr_rm_data = []
            num_at_data = []
            for config in configurations:
                num_attempts = 0
                num_successes = 0
                sr_per_scene = []
                num_rm_successes = 0

                for i in num_scenes:
                    if approach != 'nsga':
                        json_path = f'{src_dir}/{m}/{config}/{i}-0/d-{approach}/_measurementstats.json'
                    else:                        
                        json_path = f'{src_dir}/{m}/{config}/{i}-0/d-{approach}/nsga2-actors/_measurementstats.json'
                    if os.path.exists(json_path):
                        with open(json_path) as f:
                            json_data = json.load(f)
                        
                        json_res = json_data['results']
                        num_attempts += len(json_res)
                        num_successes_for_scene = 0

                        for r in json_res:
                            if r['success']:
                                num_successes += 1
                                if approach == 'nsga':
                                    num_successes_for_scene += (100/len(num_scenes))
                                if approach != 'nsga' and  r['CON_sat_%_rm'] == 1:
                                    num_rm_successes += 1
                                    num_successes_for_scene += (100/len(num_scenes))
                        sr_per_scene.append(num_successes_for_scene)

                ns_data.append(num_successes)
                succ_rate = 100*(-0.1 if num_attempts == 0 else num_successes / num_attempts)
                sr_data.append(succ_rate)                
                srps_data.append(sr_per_scene)
                ns_rm_data.append(num_rm_successes)
                succ_rm_rate = 100*(-0.1 if num_attempts == 0 else num_rm_successes / num_attempts)
                sr_rm_data.append(succ_rm_rate)
                num_at_data.append(num_attempts)

            fig1_data[approach] = {'sr':sr_data, 'srps':srps_data, 'ns':ns_data, 'at':num_at_data, 'srrm':sr_rm_data, 'nsrm':ns_rm_data}

        data[m] = fig1_data
    # FIGURE CREATION
    
    # import pprint 
    # pp = pprint.PrettyPrinter(indent=2)
    # pp.pprint(data)

    adjustSize()
    for m in maps:

        n_groups = len(configurations)
        fig, ax = plt.subplots()
        index = np.arange(n_groups)
        bar_width = 0.2

        bps = []

        for i in range(len(approaches)):
            approach = approaches[i]
            name = names_app[i]
            pos = index+i*bar_width

            vals = data[m][approach]['srps']
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
            # # attempts = data[m][approach]['at']
            # # successes = data[m][approach]['su']
            # # for j, v in enumerate(successes):
            # #     ax.text(pos[j], means[j]+math.log(2), str(v), ha='center', fontweight='bold')

            # if approach == 'nsga':
            #     vals = data[m][approach]['sr']
            #     plt.bar(pos, vals, bar_width, 
            #         # color=colors[i], 
            #         color=colors[i],
            #         # alpha=1 if approach == 'nsga' else opacity, 
            #         label=name, 
            #         edgecolor=colors[i], 
            #         hatch='//')

            # # PRINT w/ RM SAT
            # if approach != 'nsga':
            #     vals_rm = data[m][approach]['srrm']
            #     plt.bar(pos, vals_rm, bar_width, color=colors[i], alpha=1, label=name)
                
            #     # print success ratio
            #     # for i, v in enumerate(vals_rm):
            #     #     ax.text(pos[i], max(0, vals_rm[i])+1, str(round(v)), ha='center', fontweight='bold')

        plt.xlabel('Scene size')
        plt.ylabel('Success rate (%)')
        plt.ylim(0, 105)
        # plt.title(m)
        plt.xticks(index + 1.5*bar_width, ('2 actors', '3 actors', '4 actors'))
        # plt.legend()
        plt.tight_layout()
        # plt.show()
        save_path = f'{fig1_out_dir}/{m}.pdf'
        plt.savefig(save_path)

        print(f'Saved figure at {save_path}')


##########################
# FIGURE RQ2.2: Runtime Analysis
##########################
def figRQ22(stat_sig=False):
    
    fig5_out_dir = mk(f'{out_dir}/RQ2.2')

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
                    if approach != 'nsga':
                        json_path = f'{src_dir}/{m}/{config}/{i}-0/d-{approach}/_measurementstats.json'
                    else:                        
                        json_path = f'{src_dir}/{m}/{config}/{i}-0/d-{approach}/nsga2-actors/_measurementstats.json'
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
                if config == "3actors" or  config == "2actors"  :
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
                        
                        # print(statistics.median(nsga_times))
                        if len(app_times) == 0:
                            print(f'    nf  = (EMPTY)')
                        else:
                            # if config=='3actors' and approach=='sc1':
                            # print(len(nsga_times))
                            df = mwu(nsga_times, app_times, alternative=alt)
                            p=df["p-val"]["MWU"]
                            # print(df)
                            print(('~~~~' if p>thresh else '    ') + f'nf  = nsga*{approach}: (pvalue={p}) (u1={df["U-val"]["MWU"]}) (eff={df["CLES"]["MWU"]})')


                            factors = range(1, 4, 1)
                            factors=[]
                            # factors = [1+x/10 for x in range(0, 21)]
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
# FIGURE RQ2.3: Success Rate Distribution
##########################
def figRQ23():

    fig2_out_dir = mk(f'{out_dir}/RQ2.3')

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
                    if approach != 'nsga':
                        json_path = f'{src_dir}/{m}/{config}/{i}-0/d-{approach}/_measurementstats.json'
                    else:                        
                        json_path = f'{src_dir}/{m}/{config}/{i}-0/d-{approach}/nsga2-actors/_measurementstats.json'
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

    
    # import pprint 
    # pp = pprint.PrettyPrinter(indent=2)
    # pp.pprint(data)


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
        # print(hist_vals)
        plt.bar(pos, hist_vals, sub_width, color=colors[i], alpha=1 if approach == 'nsga' or add == '-rm' else opacity, label=f'{approach}{add}')


    plt.xlabel('Success rate (%)')
    plt.ylabel('Number of  Scenes')    
    plt.ylim(0, 31.5)
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



figRQ21(True, True)
figRQ21x()
figRQ22(True)
figRQ23()
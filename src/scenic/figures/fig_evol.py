
import statistics
import os
import json
from pathlib import Path

from util import adjustSize

import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import fisher_exact
from scipy.stats import ranksums
from pingouin import mwu

maps = ['zalaFullcrop']
configurations = ['2actors', '3actors', '4actors']

num_scenes = range(10) #range(10)
evol_approaches = ['ga-one', 'nsga3-categories', 'nsga3-actors', 'nsga3-none', 'nsga2-importance', 'nsga2-actors', 'nsga2-categories']
names_app = ['ga-1', 'n3-c', 'n3-a', 'n3-0', 'n2-i', 'n2-a', 'n2-c']


default = plt.rcParams['axes.prop_cycle'].by_key()['color']
colors = ['#A50205', '#0876B5', '#CC6400', '#5813B7', default[4], default[5], default[6]]
colors_light = ['#E8BFC0', '#C1DDEC', '#F2D8BF']
opacity = 0.25

base_dir = 'measurements'
data_dir = f'{base_dir}/data'
src_dir = f'{base_dir}/results'
out_dir = f'{base_dir}/figures'
Path(f'{out_dir}/').mkdir(parents=True, exist_ok=True)

timeout = 420


##########################
# FIGURE RQ1.1: Success Rate Comparison
##########################
def figRQ11(stat_sig=True, noPartial=False):
    global_out_dir = f'{out_dir}/evol'
    rt_out_dir = f'{global_out_dir}/runtime'
    sr_out_dir = f'{global_out_dir}/success-rate'
    Path(f'{rt_out_dir}/').mkdir(parents=True, exist_ok=True)
    Path(f'{sr_out_dir}/').mkdir(parents=True, exist_ok=True)

    data = {}
    for m in maps:
        fig1_data = {}

        for approach in evol_approaches:
            rt_data = [] # 2D array
            ns_data = []
            sr_data = []
            num_at_data = []
            for config in configurations:
                rt_con_data = []
                num_attempts = 0
                num_successes = 0

                for i in num_scenes:
                    json_path = f'{src_dir}/{m}/{config}/{i}-0/d-nsga/{approach}/_measurementstats.json'
                    if os.path.exists(json_path):
                        with open(json_path) as f:
                            json_data = json.load(f)
                        
                        json_res = json_data['results']
                        num_attempts += len(json_res)

                        for r in json_res:
                            if r['success']:
                                num_successes += 1
                                rt_con_data.append(r['time'])

                rt_data.append(rt_con_data)
                ns_data.append(num_successes)
                succ_rate = 100*(-0.1 if num_attempts == 0 else num_successes / num_attempts)
                sr_data.append(succ_rate)
                num_at_data.append(num_attempts)

            fig1_data[approach] = {'rt':rt_data, 'sr':sr_data, 'ns':ns_data, 'at':num_at_data}

        data[m] = fig1_data

    # import pprint 
    # pp = pprint.PrettyPrinter(indent=2)
    # pp.pprint(data)
    # exit()

    #create figs
    # adjustSize()
    for m in maps:

        n_groups = len(configurations)
        fig, ax = plt.subplots()
        index = np.arange(n_groups)
        bar_width = 0.125

        # SUCCESS RATE ANALYSIS
        for i, approach in enumerate(evol_approaches):
            name = names_app[i]
            pos = index+i*bar_width

            vals = data[m][approach]['sr']
            plt.bar(pos, vals, bar_width, 
                # color=colors[i], 
                color=colors[i],
                # alpha=1 if approach == 'nsga' else opacity, 
                label=name, 
                edgecolor=colors[i], 
                hatch='//')
                
                # print success ratio
                # for i, v in enumerate(vals_rm):
                #     ax.text(pos[i], max(0, vals_rm[i])+1, str(round(v)), ha='center', fontweight='bold')

        plt.xlabel('Scene size')
        plt.ylabel('Success rate (%)')
        # plt.title(m)
        plt.xticks(index + 1.5*bar_width, ('2 actors', '3 actors', '4 actors'))
        plt.legend()
        plt.tight_layout()
        # plt.show()
        save_path = f'{sr_out_dir}/{m}.pdf'
        plt.savefig(save_path)

        print(f'Saved figure at {save_path}')

        
        # EXPORT LEGEND
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
            legend_path = f'{global_out_dir}/legend.pdf'
            fig.savefig(legend_path, dpi="figure", bbox_inches=bbox)
            # fig.savefig(legend_path)
            print(f'Saved figure at {legend_path}')

        plt.clf()

        if stat_sig:
            print(">>>Success Rate Statistical Significance<<<")
            thresh=0.05
            print(f'Map: {m}')
            for i_c, config in enumerate(configurations):
                print(f'  Config: {config}')
                print('  Details:')
                for approach in evol_approaches:
                    at = data[m][approach]['at'][i_c]
                    ns = data[m][approach]['ns'][i_c]
                    print(f'    {approach}(at={at}, ns={ns})')

                max_l = len(max(evol_approaches, key=len))
                print('    Results:')
                for i1, a1 in enumerate(evol_approaches):
                    at_1 = data[m][a1]['at'][i_c]
                    ns_1 = data[m][a1]['ns'][i_c]
                    for a2 in evol_approaches[i1+1:]:
                        at_2 = data[m][a2]['at'][i_c]
                        ns_2 = data[m][a2]['ns'][i_c]

                        # _, pvalue = fisher_exact([[nsga_at, nsga_ns],[at, ns]])
                        # # if pvalue > thresh:
                        # #     Fore.RED
                        # print(('~~~~' if pvalue>thresh else '    ') + f'nsga*{approach}: (pvalue={pvalue})')
                        
                        # print(f'nsga: {nsga_at}/{nsga_ns} | {approach}: {at}/{nsrm}')
                        # print([[at-nsrm, nsrm],[nsga_at-nsga_ns, nsga_ns]])
                        oddsratio, pvaluerm = fisher_exact([[ns_1, at_1-ns_1],[ns_2, at_2-ns_2]])
                        print(('~~~~' if pvaluerm>thresh else '    ') + f' {a1.ljust(max_l)} * {a2.ljust(max_l)} : (pvalue={pvaluerm:.3f}) (oddsrat={oddsratio:.3f})')
                print()
            print(">>>End Statistical Significance<<<")


        # RUNTIME ANALYSIS
        bps = []
        for i, approach in enumerate(evol_approaches):
            name = names_app[i]
            pos = index+i*bar_width

            vals = data[m][approach]['rt']
            bps.append(plt.boxplot(vals, positions=pos, widths=bar_width,
                patch_artist=True,
                boxprops=dict(facecolor=colors[i],color='k'),
                capprops=dict(color='k'),
                whiskerprops=dict(color=colors[i]),
                flierprops=dict(color=colors[i], markeredgecolor=colors[i]),
                medianprops=dict(color='k'),
                labels=[approach, approach, approach]))
                
                # print success ratio
                # for i, v in enumerate(vals_rm):
                #     ax.text(pos[i], max(0, vals_rm[i])+1, str(round(v)), ha='center', fontweight='bold')

        plt.xlabel('Scene size')
        plt.ylabel('Runtime (s)')
        # plt.title(m)
        plt.xticks(index + 1.5*bar_width, ('2 actors', '3 actors', '4 actors'))
        plt.legend([bp['boxes'][0] for bp in bps], evol_approaches)
        plt.tight_layout()
        # plt.show()
        save_path = f'{rt_out_dir}/{m}.pdf'
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
            for i_c, config in enumerate(configurations):
                print(f'  Config: {config}')
                # print('  Details:')
                # for approach in evol_approaches:
                #     at = data[m][approach]['at'][i_c]
                #     ns = data[m][approach]['ns'][i_c]
                #     print(f'    {approach}(at={at}, ns={ns})')

                max_l = len(max(evol_approaches, key=len))
                print('    Results:')
                for i1, a1 in enumerate(evol_approaches):
                    at_1 = data[m][a1]['at'][i_c]
                    ns_1 = data[m][a1]['ns'][i_c]
                    rt_1 = data[m][a1]['rt'][i_c]
                    rt_1_w_fail = rt_1 + [timeout for _ in range((at_1-ns_1))]
                    assert len(rt_1) == ns_1
                    assert len(rt_1_w_fail) == at_1
                    for a2 in evol_approaches[i1+1:]:
                        at_2 = data[m][a2]['at'][i_c]
                        ns_2 = data[m][a2]['ns'][i_c]
                        rt_2 = data[m][a2]['rt'][i_c]
                        rt_2_w_fail = rt_2 + [timeout for _ in range((at_2-ns_2))]

                        # NO FAILURE
                        if len(rt_2) == 0:
                            print(f'     nf = (EMPTY)')
                        else:
                            # if config=='3actors' and approach=='sc1':
                            # print(len(nsga_times))
                            # print(statistics.median(app_times))
                            df = mwu(rt_1, rt_2, alternative=alt)
                            p=df["p-val"]["MWU"]
                            print(('~~~~' if p>thresh else '    ') + f' nf = {a1.ljust(max_l)} * {a2.ljust(max_l)} : (pvalue={p:.3f}) (u1={df["U-val"]["MWU"]}) (eff={df["CLES"]["MWU"]})')

                            # # factors = [15,16,17,18,19,20,21,22,23,24,25] # 2actors
                            # factors = [291, 292, 293, 294, 295]
                            # factors= [321, 322, 323, 324, 325]
                            # # factors = [2,3,4,5,6] # 3actors
                            # for factor in factors:
                            #     dffac = mwu(nsga_times, [factor*i for i in app_times], alternative=alt)
                            #     pfac=dffac["p-val"]["MWU"]
                            #     print(('~~~~' if pfac>thresh else '    ') + f'      fact={factor}: (pvalue={pfac}) (u1={dffac["U-val"]["MWU"]}) (eff={dffac["CLES"]["MWU"]})')

                        # NO PARTIAL
                        df = mwu(rt_1_w_fail, rt_2_w_fail, alternative=alt)
                        p=df["p-val"]["MWU"]
                        print(('~~~~' if p>thresh else '    ') + f' np = {a1.ljust(max_l)} * {a2.ljust(max_l)} : (pvalue={p:.3f}) (u1={df["U-val"]["MWU"]}) (eff={df["CLES"]["MWU"]})')
                
                
                print()
            print(">>>End Statistical Significance<<<")


figRQ11(True, False)
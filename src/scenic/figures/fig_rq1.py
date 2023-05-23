
import statistics
import os
import json
from pathlib import Path

from util import adjustSize, mk

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot

from scipy.stats import fisher_exact
from pingouin import mwu

maps = ['tram05']
configurations = ['2actors', '3actors', '4actors']

q=plt.rcParams['axes.prop_cycle'].by_key()['color']
colors = [q[2],  '#E3723D',q[4], q[5], q[6], q[7], q[8], q[9]]
colors = [q[2],   '#DBB743',q[4],q[5],q[6], q[9], q[7],'#E3723D']

num_scenes = range(10)
evol_approaches = ['nsga2-actors', 'nsga2-categImpo', 'nsga3-none', 'nsga3-categories', 'nsga3-categImpo', 'nsga3-actors', 'nsga2-importance', 'ga-one']
names_app = ['N2-A', 'N2-WC', 'N3-\u00F8', 'N3-C', 'N3-WC', 'N3-A', 'N2-WD', 'GA-G']


# default = plt.rcParams['axes.prop_cycle'].by_key()['color']
# colors = ['#A50205', '#0876B5', '#CC6400', '#5813B7', default[4], default[5], default[6], default[7]]

base_dir = 'measurements'
data_dir = f'{base_dir}/data'
src_dir = f'docker' # f'{base_dir}/results'
out_dir = f'{base_dir}/figures'
Path(f'{out_dir}/').mkdir(parents=True, exist_ok=True)

# HISTORY CONFIG
timeout = 600
history_times = [i for i in range(0, 600, 30)]


##########################
# FIGURE RQ1: Comparing various MHS Approaches
##########################
def figRQ1(stat_sig=True):

    # IN
    src_dir = 'docker/results/RQ1'
    
    # OUT DIR
    global_out_dir = 'docker/figures/RQ1'
    rt_out_dir = mk(f'{global_out_dir}/runtime')
    sr_out_dir = mk(f'{global_out_dir}/success-rate')
    if not stat_sig:
        hist_out_dir = mk(f'docker/figures/extra0/history')

    data = {}
    for m in maps:
        fig1_data = {}

        for approach in evol_approaches:
            rt_data = [] # 2D array, {num_actors * num_successful_runs}
            ns_data = []
            sr_data = []
            num_at_data = []
            hist_data = [] # 3d array, {num_actors * num_all_runs * tot_num_history points_padded}
            for config in configurations:
                rt_con_data = []
                num_attempts = 0
                num_successes = 0
                hist_con_data = []

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

                            # history
                            hist_con_res_data = r['history']
                            hist_con_res_data.reverse()
                            len_diff = len(history_times) - len(hist_con_res_data)
                            assert len_diff >= 0
                            for _ in range(len_diff):
                                hist_con_res_data.append(None)
                            hist_con_data.append(hist_con_res_data)

                rt_data.append(rt_con_data)
                hist_data.append(hist_con_data)
                ns_data.append(num_successes)
                succ_rate = 100*(-0.1 if num_attempts == 0 else num_successes / num_attempts)
                sr_data.append(succ_rate)
                num_at_data.append(num_attempts)
                
            fig1_data[approach] = {'rt':rt_data, 'sr':sr_data, 'ns':ns_data, 'at':num_at_data, 'hist':hist_data}

        data[m] = fig1_data

    # import pprint 
    # pp = pprint.PrettyPrinter(indent=2)
    # pp.pprint(data)
    # exit()

    #create figs
    adjustSize()
    for m in maps:

        n_groups = len(configurations)
        fig, ax = plt.subplots()
        index = np.arange(n_groups)
        bar_width = 0.1111

        ######################
        # SUCCESS RATE ANALYSIS
        for i, approach in enumerate(evol_approaches):
            name = names_app[i]
            pos = index+i*bar_width

            vals = data[m][approach]['sr']
            # print(vals)
            # continue
            ax.bar(pos, vals, bar_width, 
                color=colors[i], 
                # color=colors[i],
                # alpha=1 if approach == 'nsga' else opacity, 
                label=name, 
                # edgecolor=colors[i], 
                # hatch='//'
                )
        
        # #define matplotlib figure and axis
        # fig, ax = plt.subplots()

        # #create simple line plot
        # ax.plot([0, 10],[0, 20])

        # #set aspect ratio to 1
        ratio = 0.5
        x_left, x_right = ax.get_xlim()
        y_low, y_high = ax.get_ylim()
        ax.set_aspect(abs((x_right-x_left)/(y_low-y_high))*ratio)        
        
        plt.xlabel('Scene size')
        plt.ylabel('Success rate (%)')
        # plt.title(m)
        plt.xticks(index + 3.5*bar_width, ('2 actors', '3 actors', '4 actors'))
        # plt.legend()
        plt.tight_layout()
        # plt.tight_layout(pad=0)
        # plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        # plt.show()

        save_path = f'{sr_out_dir}/{m}.pdf'
        plt.savefig(save_path, bbox_inches='tight')

        print(f'Saved figure at {save_path}')

        # EXPORT LEGEND
        # legend = plt.legend(loc=3, framealpha=1, frameon=False)
        plt.axis('off')
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.2,
                        box.width, box.height * 0.9])

        # Put a legend below current axis
        legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), framealpha=1, frameon=False, ncol=4)

        # legend = plt.legend(ncol=7, framealpha=1, frameon=False)
        fig  = legend.figure
        fig.canvas.draw()
        bbox  = legend.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        legend_path = f'{sr_out_dir}/legend.pdf'
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

        ######################
        # RUNTIME ANALYSIS
        bps = []
        fig, ax = plt.subplots()
        for i, approach in enumerate(evol_approaches):
            name = names_app[i]
            pos = index+i*bar_width

            vals = data[m][approach]['rt']
            # bps.append(ax.boxplot(vals, positions=pos, widths=bar_width,
            #     patch_artist=True,
            #     boxprops=dict(facecolor=colors[i],color='k'),
            #     capprops=dict(color='k'),
            #     whiskerprops=dict(color=colors[i]),
            #     flierprops=dict(color=colors[i], markeredgecolor=colors[i]),
            #     medianprops=dict(color='k'),
            #     labels=[approach, approach, approach]))
            
            ax.boxplot(vals, positions=pos, widths=bar_width,
                patch_artist=True,
                boxprops=dict(facecolor=colors[i],color='k'),
                capprops=dict(color='k'),
                whiskerprops=dict(color=colors[i]),
                flierprops=dict(color=colors[i], markeredgecolor=colors[i]),
                medianprops=dict(color='k'),
                labels=[approach, approach, approach])
                
                # print success ratio
                # for i, v in enumerate(vals_rm):
                #     ax.text(pos[i], max(0, vals_rm[i])+1, str(round(v)), ha='center', fontweight='bold')


        ratio = 0.5
        x_left, x_right = ax.get_xlim()
        y_low, y_high = ax.get_ylim()
        ax.set_aspect(abs((x_right-x_left)/(y_low-y_high))*ratio)

        plt.xlabel('Scene size')
        plt.ylabel('Runtime (s)')
        # plt.title(m)
        plt.xticks(index + 3.5*bar_width, ('2 actors', '3 actors', '4 actors'))
        # plt.legend([bp['boxes'][0] for bp in bps], evol_approaches)
        plt.tight_layout()
        # plt.show()
        save_path = f'{rt_out_dir}/{m}.pdf'
        plt.savefig(save_path, bbox_inches='tight')

        print(f'Saved figure at {save_path}')
        plt.clf()

        if stat_sig:
            alt = "less"
            # alt = "greater"
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
                print(f'    Results ({alt}):')
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
                            u = df["U-val"]["MWU"]
                            eff = df["CLES"]["MWU"]

                        # NO PARTIAL
                        df_np = mwu(rt_1_w_fail, rt_2_w_fail, alternative=alt)
                        p_np=df_np["p-val"]["MWU"]
                        u_np = df_np["U-val"]["MWU"]
                        eff_np = df_np["CLES"]["MWU"]
                            
                        print(f'{"~~" if p>thresh else "  "}{"~~" if p_np>thresh else "  "} {a1.ljust(max_l)} * {a2.ljust(max_l)} : NoFailures [p={p:.3f}, u1={int(u):04d}, eff={eff:.3f}], FailsAsTimeOut [p={p_np:.3f}, u1={int(u_np):04d}, eff={eff_np:.3f}]')

                            # # factors = [15,16,17,18,19,20,21,22,23,24,25] # 2actors
                            # factors = [291, 292, 293, 294, 295]
                            # factors= [321, 322, 323, 324, 325]
                            # # factors = [2,3,4,5,6] # 3actors
                            # for factor in factors:
                            #     dffac = mwu(nsga_times, [factor*i for i in app_times], alternative=alt)
                            #     pfac=dffac["p-val"]["MWU"]
                            #     print(('~~~~' if pfac>thresh else '    ') + f'      fact={factor}: (pvalue={pfac}) (u1={dffac["U-val"]["MWU"]}) (eff={dffac["CLES"]["MWU"]})')

                        # print(('~~~~' if p>thresh else '    ') + f' np = {a1.ljust(max_l)} * {a2.ljust(max_l)} : (pvalue={p:.3f}) (u1={df_np["U-val"]["MWU"]}) (eff={df_np["CLES"]["MWU"]})')
                
                
                print()
            print(">>>End Statistical Significance<<<")

        if stat_sig:
            exit()
        
        ######################
        # HISTORY ANALYSIS

        data_types = ["least_con_vio", "gd", "igd", "min_f_sum"]
        data_type_cleanups = [False, True, True, True]
        keep_only_timeout = True

        for approach in evol_approaches:
            for data_t in data_types:
                Path(f'{hist_out_dir}/{data_t}/{approach}/').mkdir(parents=True, exist_ok=True)

        for conf_id, config in enumerate(configurations):
            # ['2actors', '3actors', '4actors']
            Path(f'{hist_out_dir}/success/{config}/').mkdir(parents=True, exist_ok=True)

            for i, approach in enumerate(evol_approaches):
                config_data = data[m][approach]['hist'][conf_id]
                if len(config_data) == 0:
                    continue

                # HANDLE increase of ccess rate
                num_successes_sequence = [0 for _ in range(len(history_times))]
                for run_data in config_data:
                    # for a single run, sequence of history entries
                    for hist_pt_i, hist_pt in enumerate(run_data):
                        if hist_pt == None:
                            num_successes_sequence[hist_pt_i] += 1

                # make_ratio
                tot_at = data[m][approach]['at'][conf_id]
                num_successes_sequence = [i/tot_at for i in num_successes_sequence]

                # Create success rate fig
                plt.bar(history_times, num_successes_sequence, color='0.9', edgecolor='0.7', width=history_times[1]-history_times[0])
                plt.ylabel('Success rate', color='0.5') 
                plt.ylim(0, 1)

                plt.xlabel('time')
                plt.xticks(history_times, rotation=45)
                plt.title(f'{m}-{config}-Success-Rate')
                # plt.yscale('log')
                plt.tight_layout()
                # plt.show()
                save_path = f'{hist_out_dir}/success/{config}/{m}-{approach}.pdf'
                plt.savefig(save_path)

                print(f'Saved figure at {save_path}')
                plt.clf()

                # continue

                # HANDLE metric value sequence
                for data_t_i, data_t in enumerate(data_types):
                    
                    # Add bar chart for success rates
                    ax1 = host_subplot(111, adjustable='box')
                    ax1.bar(history_times, num_successes_sequence, color='0.9', edgecolor='0.7', width=history_times[1]-history_times[0])
                    ax1.set_ylabel('Success rate', color='0.5') 
                    ax1.set_ylim(0, 1)

                    # Prep metrics figure
                    ax2 = plt.twinx()

                    max_metric_val = -1
                    for run_data in config_data:
                        all_data = run_data[-1] != None
                        if all_data or not keep_only_timeout :
                            data_seq = [i[data_t] if not i == None else 0 for i in run_data]
                            data_seq_2 = [i[data_t] for i in run_data if i is not None]

                            if data_type_cleanups[data_t_i]:
                                
                                # CUT OFF THINGS FURTHER THAN 2 std-devs away
                                med_2 = statistics.median(data_seq)
                                if med_2 == 0:
                                    sd_multiplier = 0
                                else:
                                    sd_multiplier = 1
                                    
                                med = statistics.median(data_seq_2)
                                if len(data_seq_2) > 1:
                                    sd = statistics.stdev(data_seq_2)
                                    data_seq = [i if i <= med+sd_multiplier*sd else None for i in data_seq]

                                # OPTION 2
                                # med = statistics.median(data_seq[-len(data_seq):])
                                # data_seq = [i if i <= med*2 else None for i in data_seq]

                                # NORMALIZE remaining data to 0..1
                                data_seq_sum = max(i for i in data_seq if i is not None)
                                data_seq = [float(i)/data_seq_sum if i != None else None for i in data_seq]
                                # print(sum(1 for i in data_seq if i == 1))

                            ax2.plot(history_times, data_seq, linewidth=2)
                            cur_max = max(x for x in data_seq if x is not None)
                            if max_metric_val < cur_max:
                                max_metric_val = cur_max

                    plt.xlabel('time')
                    plt.xticks(history_times, rotation=45)
                    plt.title(f'{m}-{config}-{approach}')
                    ax2.set_ylim(0, max_metric_val)
                    ax2.set_ylabel(data_t)
                    # plt.yscale('log')
                    plt.tight_layout()
                    # plt.show()
                    save_path = f'{hist_out_dir}/{data_t}/{approach}/{m}-{config}.pdf'
                    plt.savefig(save_path)

                    print(f'Saved figure at {save_path}')
                    plt.clf()
            # TODO create aggregate figure

figRQ1()

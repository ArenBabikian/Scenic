
import statistics
import os
import json
from pathlib import Path

from util import adjustSize, mk

import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import fisher_exact
from pingouin import mwu

# DATA CONFIG
m = 'zalaFullcrop'
approach = 'nsga'
configs = ['none', 'r', 'rc', 'rcp', 'rcpd', 'rcpdv']
names = ['\u00F8\n[0..0]', 'R\n[4..4]', 'RC\n[10..10]', 'RCP\n[16..22]', 'RCPD\n[22..28]', 'RCPDV\n[24..33]']
# mhsConfigs = ['nsga2-categImpo', 'nsga2-actors', 'nsga2-actors']
mhsConfigs = ['nsga2-categImpo', 'nsga2-actors', 'nsga3-categories']

# FIGURE CONFIG
q = plt.rcParams['axes.prop_cycle'].by_key()['color']
colors = [q[2], '#DBB743',q[5]]

# SAVE CONFIG
src_dir = 'docker/results/RQ3'
out_dir = mk(f'docker/figures/RQ3')

##########################
# FIGURE RQ3: performance vs. Number of Constraints DATA
##########################
def figRQ3():

    # DATA GATHERING
    allData = {}
    for mhsc in mhsConfigs:
        data = {}
        for j in range(len(configs)):
            c = configs[j]
            config_data = {'num_att':0, 'num_succ':0, 'times_succ':[], }

            for i in range(10):
                # id, numcons, succ rate, median time
                json_path = f'{src_dir}/{m}/cons/{c}/{i}/{mhsc}/_measurementstats.json'

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
                else:
                    print(f'Did not find file at {json_path}')
                    exit()

                config_data["median_time"] = -1 if not config_data['times_succ'] else statistics.median(config_data['times_succ'])
            data[names[j]] = config_data
        allData[mhsc] = data


    allPlotData = {}
    for mhsc in mhsConfigs:
        plot_data = {'nm':[], 'sr':[], 'rt':[], 'new_ns':[], 'new_at':[], 'new_rt':[]}
        data = allData[mhsc] 
        for x in data:
            plot_data['nm'].append(x)
            plot_data['sr'].append(100* data[x]['num_succ'] / data[x]['num_att'])
            plot_data['rt'].append(data[x]['median_time'])
            plot_data['new_ns'].append(data[x]['num_succ'])
            plot_data['new_at'].append(data[x]['num_att'])
            plot_data['new_rt'].append(data[x]['times_succ'])
        allPlotData[mhsc]=plot_data


    # FIGURE CREATION

    # import pprint 
    # pp = pprint.PrettyPrinter(indent=2)
    # pp.pprint(data)
    # pp.pprint(plot_data)

    # STATISTICAL SIGNIFICANCE
    print(">>>Statistical Significance<<<")
    print("(RT measurements are two-sided)")
    thresh=0.05
    print(f'Map: {m}')
    for i_c, config in enumerate(configs):
        print(f'  Config: {config}')
        print('  Details:')
        for a in mhsConfigs:
            sr = allPlotData[a]['sr'][i_c]
            # rt = data[m][approach]['rt'][i_c]
            print(f'    {a}(sr={sr})')

        max_l = len(max(mhsConfigs, key=len))
        print('    Results:')
        for i1, a1 in enumerate(mhsConfigs):
            ns_1 = allPlotData[a1]['new_ns'][i_c]
            at_1 = allPlotData[a1]['new_at'][i_c]
            rt_1 = allPlotData[a1]['new_rt'][i_c]
            assert len(rt_1) == int(ns_1)
            for a2 in mhsConfigs[i1+1:]:
                ns_2 = allPlotData[a2]['new_ns'][i_c]
                at_2 = allPlotData[a2]['new_at'][i_c]
                rt_2 = allPlotData[a2]['new_rt'][i_c]
                oddsratio, pvaluerm = fisher_exact([[ns_1, at_1-ns_1],[ns_2, at_2-ns_2]])
                print(('~~~~' if pvaluerm>thresh else '    ') + f' SR {a1.ljust(max_l)} * {a2.ljust(max_l)} : (pvalue={pvaluerm:.3f}) (oddsrat={oddsratio:.3f})')


                alt="two-sided"
                if len(rt_2) == 0 or len(rt_1) == 0:
                    print(f'     RT (EMPTY)')
                else:
                    # if config=='3actors' and approach=='sc1':
                    # print(len(nsga_times))
                    # print(statistics.median(app_times))
                    # print(rt_1)
                    # print(rt_2)
                    df = mwu(rt_1, rt_2, alternative=alt)
                    p=df["p-val"]["MWU"]
                    u = df["U-val"]["MWU"]
                    eff = df["CLES"]["MWU"]
                    print(f'{"~~~~" if p>thresh else "    "} RT{"".ljust(max_l*2+4)} : (p={p:.3f}, u1={int(u):04d}, eff={eff:.3f})')

                # print('-----------')
        print()
    print(">>>End Statistical Significance<<<")

    # exit()

    def f1():
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
        bar_width = 1/(2*len(mhsConfigs)+1)
        labels=['Success Rate (%)', 'Median Runtime (s)']

        color = '#2F9E00'
        ax1.set_ylabel(labels[0], color=color)
        # ax1.set_ylim(bottom=0)
        for i, mhsc in enumerate(mhsConfigs):
            color = '#2F9E00'
            color = colors[i]
            bar1 = ax1.bar(index+i*bar_width, allPlotData[mhsc]['sr'], bar_width, 
                label=labels[0], color=color)
            
        # bar1 = ax1.bar(index, plot_data['sr'], bar_width, 
        #     label=labels[0], color=color)
        ax1.tick_params(axis='y', labelcolor=color)
        
        ax2 = plt.twinx()
        # ax2.set_ylim(bottom=0)
        color = '#0020A2'
        ax2.set_ylabel(labels[1], color=color)
        # bar2 = ax2.bar(index+bar_width, [-1 if len(rt)==0 else statistics.median(rt) for rt in plot_data['rt']], bar_width,label=labels[1], color=color)
        
        # bar2 = ax2.bar(index+bar_width, plot_data['rt'], bar_width, label=labels[1], color=color)
        for i, mhsc in enumerate(mhsConfigs):
            
            color = '#0020A2'
            color = colors[i]
            bar2 = ax2.bar(index+(len(mhsConfigs)+i)*bar_width, allPlotData[mhsc]['rt'], bar_width,
            alpha=0.25, label=labels[1], color=color, hatch='//')

        ax2.tick_params(axis='y', labelcolor=color) 
        fix_ratio(ax1, ax1)
        fix_ratio(ax2, ax2)
        
        plt.xlabel('Included constraint types and number')
        plt.xticks(index + (len(mhsConfigs)-0.5)*bar_width, tuple(names))
        # plt.legend([bar1, bar2], labels, loc=6)

        # plt.show()
        save_path = f'{out_dir}/{m}.pdf'
        plt.savefig(save_path, bbox_inches='tight')
        print(f'Saved figure at {save_path}')
    
    def f2():

        adjustSize(s=12) 
        ratio = 0.4
        n_groups = len(configs)
        fig, ax = plt.subplots()
        index = np.arange(n_groups)
        bar_width = 1/(len(mhsConfigs)+1)
        # labels=['Success Rate (%)', 'Median Runtime (s)']
        labels = ['N2-WC', 'N2-A', 'N3-C']

        for i, mhsc in enumerate(mhsConfigs):
            color = '#2F9E00'
            color = colors[i]
            bar1 = ax.bar(index+i*bar_width, allPlotData[mhsc]['sr'], bar_width, color=color, label=labels[i])

        x_left, x_right = ax.get_xlim()
        y_low, y_high = ax.get_ylim()
        ax.set_aspect(abs((x_right-x_left)/(y_low-y_high))*ratio) 
        
        plt.xlabel('Included constraint types and number')
        plt.xticks(index + (-0.5+len(mhsConfigs)/2.0)*bar_width, tuple(names))
        plt.ylabel('Success rate (%)')
        # plt.legend([bar1, bar2], labels, loc=9)

        # plt.tight_layout()
        # plt.show()
        save_path = f'{out_dir}/{m}-sr.pdf'
        plt.savefig(save_path, bbox_inches='tight')

        print(f'Saved figure at {save_path}')
        
        ###############
        # EXPORT LEGEND
        # legend = plt.legend(loc=3, framealpha=1, frameon=False)
        plt.axis('off')
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.2,
                        box.width, box.height * 0.9])

        # Put a legend below current axis
        legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), framealpha=1, frameon=False, ncol=3)

        # legend = plt.legend(ncol=7, framealpha=1, frameon=False)
        fig  = legend.figure
        fig.canvas.draw()
        bbox  = legend.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        legend_path = f'{out_dir}/legend.pdf'
        fig.savefig(legend_path, dpi="figure", bbox_inches=bbox)
        # fig.savefig(legend_path)
        print(f'Saved figure at {legend_path}')
        plt.clf()

        #FIGURE 2
        adjustSize(s=12)
        n_groups = len(configs)
        fig, ax = plt.subplots()
        index = np.arange(n_groups)
        bar_width = 1/(len(mhsConfigs)+1)

        for i, mhsc in enumerate(mhsConfigs):
            color = '#2F9E00'
            color = colors[i]
            ##############
            # THIS FOR BAR
            # bar2 = ax.bar(index+i*bar_width, 
            #               [0 if len(rt)==0 else statistics.median(rt) for rt in allPlotData[mhsc]['new_rt']], 
            #               bar_width,
            #             #   alpha=0.5,
            #               label=labels[i],
            #               color=color,
            #             #   hatch='//'
            #               )
            ##############
            # THIS FOR BOX
            ax.boxplot(allPlotData[mhsc]['new_rt'],
                       positions=index+i*bar_width,
                       widths=bar_width,
                       patch_artist=True,
                       boxprops=dict(facecolor=colors[i],color='k'),
                       capprops=dict(color='k'),
                       whiskerprops=dict(color=colors[i]),
                       flierprops=dict(color=colors[i], markeredgecolor=colors[i]),
                       medianprops=dict(color='k'))     
        x_left, x_right = ax.get_xlim()
        y_low, y_high = ax.get_ylim()
        ax.set_aspect(abs((x_right-x_left)/(y_low-y_high))*ratio) 
        
        plt.xlabel('Included constraint types and number')
        plt.xticks(index + (-0.5+len(mhsConfigs)/2.0)*bar_width, tuple(names))
        plt.ylabel('Median Runtime (s)')
        # plt.yticks(np.arange(0, 601, 150))
        plt.yticks(np.arange(0, 301, 50))
        # plt.legend([bar1, bar2], labels, loc=9)

        # plt.tight_layout()
        # plt.show()
        save_path = f'{out_dir}/{m}-rt-box.pdf'

        plt.savefig(save_path, bbox_inches='tight')

        print(f'Saved figure at {save_path}')

        plt.clf()

    f1()
    f2()

figRQ3()
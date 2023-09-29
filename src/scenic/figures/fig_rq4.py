
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
configurations = ['4actors', '5actors', '6actors', '7actors']
mhsConfigs = ['nsga2-categImpo', 'nsga2-actors', 'nsga2-actors']
mhsConfigs = ['nsga2-categImpo', 'nsga2-actors', 'nsga3-categories']

# FIGURE CONFIG
q = plt.rcParams['axes.prop_cycle'].by_key()['color']
# colors = [q[2],  '#E3723D',q[4], q[5], q[6], q[7], q[8], q[9]]
# colors = [q[2],  '#E3723D', q[5]]
colors = [q[2], '#DBB743',q[5]]

# SAVE CONFIG
src_dir = 'docker/results/RQ4'
out_dir = mk(f'docker/figures/RQ4')
# colors = ['#A50205', '#0876B5', '#CC6400', '#5813B7', default[4], default[5], default[6]]



##########################
# FIGURE RQ4: Scalability wrt. number of actors
##########################
def figRQ4():

    # DATA GATHERING
    allData = {}
    for mhsc in mhsConfigs:
        data = {'rt':[], 'sr':[], 'srps':[]}
        for config in configurations:
            rt_con_data = []
            num_attempts = 0 #obs
            num_successes = 0 #obs
            srps_for_config = []

            for i in range(10):
                # docker\results\RQ4\zalaFullcrop\4actors\0-0\d-nsga\nsga2-categImpo\_measurementstats.json
                json_path = f'{src_dir}/{m}/{config}/{i}-0/d-{approach}/{mhsc}/_measurementstats.json'
                if os.path.exists(json_path):
                    with open(json_path) as f:
                        json_data = json.load(f)
                    
                    json_res = json_data['results']
                    num_attempts += len(json_res)
                    sr_per_scene = 0

                    for r in json_res:
                        if r['success']:
                            # rt_con_data.append(r['time']) # TEMP RMed
                            num_successes += 1
                            rt_con_data.append(r['time'])
                            sr_per_scene += 20
                    srps_for_config.append(sr_per_scene)

            succ_rate = 100*(-0.1 if num_attempts == 0 else num_successes / num_attempts)

            data['rt'].append(rt_con_data)
            data['sr'].append(succ_rate)
            data['srps'].append(srps_for_config)
        allData[mhsc] = data

    # print(allData)

    # STATISTICAL SIGNIFICANCE
    print(">>>Statistical Significance<<<")
    print("(RT measurements are two-sided)")
    thresh=0.05
    print(f'Map: {m}')
    for i_c, config in enumerate(configurations):
        print(f'  Config: {config}')
        print('  Details:')
        for a in mhsConfigs:
            sr = allData[a]['sr'][i_c]
            # rt = data[m][approach]['rt'][i_c]
            print(f'    {a}(sr={sr})')

        max_l = len(max(mhsConfigs, key=len))
        print('    Results:')
        for i1, a1 in enumerate(mhsConfigs):
            sr_1 = allData[a1]['sr'][i_c]
            ns_1 = 25*sr_1/100
            rt_1 = allData[a1]['rt'][i_c]
            assert len(rt_1) == int(ns_1)
            for a2 in mhsConfigs[i1+1:]:
                sr_2 = allData[a2]['sr'][i_c]
                ns_2 = 25*sr_2/100
                rt_2 = allData[a2]['rt'][i_c]
                oddsratio, pvaluerm = fisher_exact([[ns_1, 25-ns_1],[ns_2, 25-ns_2]])
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

    def f1():
        # FIGURE CREATION 1
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
        bar_width = 1/(2*len(mhsConfigs)+1)
        labels=['Success Rate (%)', 'Median Runtime (s)']

        color = '#2F9E00'
        
        ax1.set_ylabel(labels[0], color=color)
        # ax1.set_ylim(bottom=0)

        for i, mhsc in enumerate(mhsConfigs):
            color = '#2F9E00'
            color = colors[i]
            bar1 = ax1.bar(index+i*bar_width, allData[mhsc]['sr'], bar_width, 
                label=labels[0], color=color)
        ax1.tick_params(axis='y', labelcolor=color)
        
        ax2 = plt.twinx()
        # ax2.set_ylim(bottom=0)
        ax2.set_ylabel(labels[1], color=color)
        
        for i, mhsc in enumerate(mhsConfigs):
            
            color = colors[i]
            # print([0 if len(rt)==0 else statistics.median(rt) for rt in allData[mhsc]['rt']])
            bar2 = ax2.bar(index+(len(mhsConfigs)+i)*bar_width,
                           [0 if len(rt)==0 else statistics.median(rt) for rt in allData[mhsc]['rt']],
                           bar_width,
                           alpha=0.5,
                           label=labels[1],
                           color=color,
                           hatch='//')
            
            # ax2.boxplot(allData[mhsc]['rt'],
            #            positions=index+(len(mhsConfigs)+i)*bar_width,
            #            widths=bar_width,
            #            patch_artist=True,
            #            boxprops=dict(facecolor=colors[i],color='k', alpha=0.5),
            #            capprops=dict(color='k'),
            #            whiskerprops=dict(color=colors[i]),
            #            flierprops=dict(color=colors[i], markeredgecolor=colors[i]),
            #            medianprops=dict(color='k')
        #            )    
            
        ax2.tick_params(axis='y', labelcolor=color) 
        fix_ratio(ax1, ax1)
        fix_ratio(ax2, ax2)
        
        plt.xlabel('Scene size')
        plt.xticks(index + (len(mhsConfigs)-0.5)*bar_width, tuple(configurations))
        # plt.legend([bar1, bar2], labels, loc=9)

        # plt.tight_layout()
        # plt.show()
        save_path = f'{out_dir}/{m}.pdf'
        plt.savefig(save_path, bbox_inches='tight')

        print(f'Saved figure at {save_path}')

    def f2():

        adjustSize(s=12) 
        # ratio = 0.666
        ratio = 0.4
        n_groups = len(configurations)
        fig, ax = plt.subplots()
        # from mpl_toolkits.axes_grid1 import host_subplot
        # ax1 = host_subplot(111, adjustable='box')
        index = np.arange(n_groups)
        bar_width = 1/(len(mhsConfigs)+1)
        labels=['Success Rate (%)', 'Median Runtime (s)']

        for i, mhsc in enumerate(mhsConfigs):
            color = '#2F9E00'
            color = colors[i]
            bar1 = ax.bar(index+i*bar_width, allData[mhsc]['sr'], bar_width, color=color)

        x_left, x_right = ax.get_xlim()
        y_low, y_high = ax.get_ylim()
        ax.set_aspect(abs((x_right-x_left)/(y_low-y_high))*ratio) 
        
        plt.xlabel('Scene size')
        plt.xticks(index + (-0.5+len(mhsConfigs)/2.0)*bar_width, tuple(configurations))
        plt.ylabel('Success rate (%)')
        # plt.legend([bar1, bar2], labels, loc=9)

        # plt.tight_layout()
        # plt.show()
        save_path = f'{out_dir}/{m}-sr.pdf'
        plt.savefig(save_path, bbox_inches='tight')

        print(f'Saved figure at {save_path}')
        plt.clf()

        #FIGURE 2
        adjustSize(s=12)
        n_groups = len(configurations)
        fig, ax = plt.subplots()
        # from mpl_toolkits.axes_grid1 import host_subplot
        # ax1 = host_subplot(111, adjustable='box')
        index = np.arange(n_groups)
        bar_width = 1/(len(mhsConfigs)+1)
        labels=['Success Rate (%)', 'Median Runtime (s)']

        for i, mhsc in enumerate(mhsConfigs):
            color = '#2F9E00'
            color = colors[i]
            ##############
            # THIS FOR BAR
            bar2 = ax.bar(index+i*bar_width, 
                          [0 if len(rt)==0 else statistics.median(rt) for rt in allData[mhsc]['rt']], 
                          bar_width,
                        #   alpha=0.5,
                          label=labels[1],
                          color=color,
                        #   hatch='//'
                          )
            ##############
            # THIS FOR BOX
            # ax.boxplot(allData[mhsc]['rt'],
            #            positions=index+i*bar_width,
            #            widths=bar_width,
            #            patch_artist=True,
            #            boxprops=dict(facecolor=colors[i],color='k'),
            #            capprops=dict(color='k'),
            #            whiskerprops=dict(color=colors[i]),
            #            flierprops=dict(color=colors[i], markeredgecolor=colors[i]),
            #            medianprops=dict(color='k'))     
        x_left, x_right = ax.get_xlim()
        y_low, y_high = ax.get_ylim()
        ax.set_aspect(abs((x_right-x_left)/(y_low-y_high))*ratio) 
        
        plt.xlabel('Scene size')
        plt.xticks(index + (-0.5+len(mhsConfigs)/2.0)*bar_width, tuple(configurations))
        plt.ylabel('Median Runtime (s)')
        # plt.legend([bar1, bar2], labels, loc=9)
        plt.yticks(np.arange(0, 5001, 1000))

        # plt.tight_layout()
        # plt.show()
        save_path = f'{out_dir}/{m}-rt-med.pdf'
        plt.savefig(save_path, bbox_inches='tight')

        print(f'Saved figure at {save_path}')
        plt.clf()

    def f3():

        #FIGURE 3
        adjustSize(s=12)
        ratio = 0.4
        n_groups = len(configurations)
        fig, ax = plt.subplots()
        index = np.arange(n_groups)
        bar_width = 1/(len(mhsConfigs)+1)

        for i, mhsc in enumerate(mhsConfigs):
            color = '#2F9E00'
            color = colors[i]
            ax.boxplot(allData[mhsc]['srps'],
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
        
        plt.xlabel('Scene size')
        plt.xticks(index + (-0.5+len(mhsConfigs)/2.0)*bar_width, tuple(configurations))
        plt.ylabel('Success Rate (%)')
        save_path = f'{out_dir}/{m}-srps.pdf'
        plt.savefig(save_path, bbox_inches='tight')

        print(f'Saved figure at {save_path}')
        plt.clf()


    f1()
    f2()
    f3()

figRQ4()
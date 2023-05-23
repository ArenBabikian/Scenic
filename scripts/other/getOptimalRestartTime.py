
from copy import Error
import statistics
import os
import json
from pathlib import Path
import seaborn as sns
import pandas as pd
import math
from colorama import Fore, Back, Style

import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import fisher_exact
from scipy.stats import chisquare
from scipy.stats import mannwhitneyu
from scipy.stats import wilcoxon


maps = ['zalaFullcrop']
configurations = ['2actors', '3actors', '4actors']
# configurations = ['4actors']
num_scenes = range(10) #range(10)

total_times = range(600, 10801, 300)



base_dir = 'meas-off'
src_dir = f'{base_dir}/results'


##########################
# FIGURE 5: Runtime Analysis
##########################
def find_best_restart_time():

    for m in maps:
        for config in configurations:
            all_suc_times = []
            all_con_nums = []
            n_attempts = 0 #obs

            for i in num_scenes:
                json_path = f'{src_dir}/{m}/{config}/{i}-0/d-nsga/_measurementstats.json'
                if os.path.exists(json_path):
                    with open(json_path) as f:
                        json_data = json.load(f)
                    
                    json_res = json_data['results']
                    n_attempts += len(json_res)

                    for r in json_res:
                        all_con_nums.append(r['CON_num'])
                        if r['success']:
                            all_suc_times.append(r['time'])

            # all_suc_times is structured such that x[i] is the time, and i is the number of successes at that time 
            avg_cons = statistics.mean(all_con_nums)
            print(f'>>>{m} - {config} - {avg_cons} constraints<<<')

            all_suc_times.sort()
            print(statistics.mean(all_suc_times))
            print(statistics.median(all_suc_times))




            for total_time in total_times:

                max_tot_solved = -1
                best_restart_time = -1

                for n_suc in range(1, len(all_suc_times)+1):
                    res_t = all_suc_times[n_suc-1]

                    res_suc_rate = n_suc/n_attempts

                    #if we take t as the restart time
                    time_left = total_time
                    total_n_suc = 0
                    unsolved_problems = n_attempts
                    while time_left > res_t:
                        n_solved = res_suc_rate * unsolved_problems

                        total_n_suc += n_solved
                        unsolved_problems -= n_solved              
                        time_left -= res_t
                        # print(f'remainingProblems={unsolved_problems}, timeleft={time_left}')   

                    s1 = total_n_suc 
                    s2 = -1
                    # How many can be solved in the remaining time?
                    # THIS IS MAKING THE SOLUTION TOO SPECIFIC
                    # for i in range(len(all_suc_times)):
                    #     res_t = all_suc_times[i]
                    #     if all_suc_times[i] > time_left:
                    #         total_n_suc += i
                    #         s2 = i
                    #         break

                    if total_n_suc >= max_tot_solved:
                        max_tot_solved = total_n_suc
                        best_restart_time = res_t
                    # print(f'res={res_t}, solved_1={s1}, solved_2={s2}, tot_solved={total_n_suc}')

                print(f'~~~tot_time={total_time}, best_res_time={best_restart_time}, tot_solved={max_tot_solved}')

find_best_restart_time()



import matplotlib.pyplot as plt

def adjustSize(ax=plt, s=14):
    # ax.tick_params(axis='both', labelsize=MED_SIZE)
    
    ax.rc('font', size=s)         
    ax.rc('axes', titlesize=s)    
    ax.rc('axes', labelsize=s)
    ax.rc('xtick', labelsize=s)
    ax.rc('ytick', labelsize=s)
    ax.rc('legend', fontsize=s)
    ax.rc('figure', titlesize=s)
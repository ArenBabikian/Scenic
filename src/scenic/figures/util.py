

from pathlib import Path
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


def mk(path):
    Path(f'{path}/').mkdir(parents=True, exist_ok=True)
    return path
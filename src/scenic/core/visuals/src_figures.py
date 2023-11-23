
import math
from scenic.core.map.map_visualisation_utils import showPairwiseCollidingRegions, zoomToIntersection
from scenic.core.visuals.utils import clean_fig, save_show_clear, show_arrows, show_carla_intersection, show_cl, show_network_alt, show_reg


def figs_src(scene, dirPath=None, view=False):
    """Render a schematic of the scene for debugging."""
    
    import matplotlib.pyplot as plt
    # SETUP
    green = '#009900'
    blue = '#0066CC'
    red = '#990000'

    r1 = scene.workspace.network.elements['road93_lane0']
    r2 = scene.workspace.network.elements['road102_lane0']

    # ###############
    # FIG 1 : lane regions
    # scene.workspace.show(plt)
    show_network_alt(scene.workspace.network, plt)

    # Add regions
    show_reg(plt, r1, blue)
    show_reg(plt, r2, green)
    showPairwiseCollidingRegions([r1, r2], plt, red)
    zoomToIntersection(scene, plt, 3)

    # save and view
    save_show_clear(plt, f'{dirPath}/fig1.png', view)

    # ###############
    # FIG 2 : exact paths
    show_network_alt(scene.workspace.network, plt)

    # Show paths
    show_cl(plt, r1.centerline, blue)
    show_arrows(plt, r1.centerline, blue, rmFirst=True)

    show_cl(plt, r2.centerline, green)
    show_arrows(plt, r2.centerline, green, rmFirst=True)

    # Add collision point
    plt.plot(88.88, -326.58, 'o', markersize=20, color=red, markeredgecolor='white', markeredgewidth=2, zorder=200)
    
    zoomToIntersection(scene, plt, 3)

    # save and view
    save_show_clear(plt, f'{dirPath}/fig2.png', view)

    # ###############
    # FIG 3 : CARLA integration
    actors = [
        {'position': (86.26, -328.67), 'color': green},
        {'position': (93.77,-326.63), 'color': blue},
    ]
    show_carla_intersection(actors)


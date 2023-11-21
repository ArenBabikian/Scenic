
import math
from scenic.core.map.map_visualisation_utils import showPairwiseCollidingRegions, zoomToIntersection
from scenic.core.regions import PolylineRegion
from scenic.core.visuals.utils import clean_fig, save_show_clear, show_arrows, show_carla_intersection, show_cl, show_network_alt, show_object, show_reg, show_regions


def figs_issta(scene, dirPath=None, view=False):
    """Render a schematic of the scene for debugging."""


    # SETUP
    red = '#c25c55' # 194,92,85
    car_red = '#A8001B' # 140,61,54
    dark_red = '#9B2721'

    blue = '#4b779d' # 75,119,157
    car_blue = '#2663E6' # 45,77,111
    dark_blue = '#283F52'

    white = '#FFFFFF'
    gray = '#808080'

    # ###############
    # FIG 1 : CARLA sample scenario

    actors = [
        {'position': (84.42, -329.82), 'color': dark_red, 'model': 'vehicle.mercedes.coupe_2020'},
        {'position': (97.77,-326.63), 'color': car_blue, 'model': 'vehicle.mercedes.coupe_2020'},
    ]
    # show_carla_intersection(actors)

    # ###############
    # FIG 2.1 : Scenario at logical levels of abstraction
    
    import matplotlib.pyplot as plt
    r1 = scene.workspace.network.elements['road93_lane0']
    full_r1 = [r1.predecessor, r1, r1.successor]
    full_cl1 = PolylineRegion.unionAll([l.centerline for l in full_r1])

    r2 = scene.workspace.network.elements['road102_lane0']
    full_r2 = [r2.predecessor, r2, r2.successor]
    full_cl2 = PolylineRegion.unionAll([l.centerline for l in full_r2])

    zoom_margins = (7, 15, 2, 5)

    # Add regions
    show_regions(plt, full_r1, blue)
    show_regions(plt, full_r2, red)
    showPairwiseCollidingRegions([r1, r2], plt, gray)
    
    show_network_alt(scene.workspace.network, plt)

    # Add arrows
    show_arrows(plt, full_cl1, white, pointsDelts=5, size=1.5)
    show_arrows(plt, full_cl2, white, pointsDelts=5, size=1.5)

    # save and view
    zoomToIntersection(scene, plt, zoom_margins)
    save_show_clear(plt, f'{dirPath}/fig21.png', view)

    # ###############
    # FIG 2.2 : Scenario at concrete levels of abstraction
    
    show_network_alt(scene.workspace.network, plt)

    def tail(reg, d):
        cl = reg.centerline
        # assert len(cl.points) == 2, f'Only works for straight roads. road has {len(cl.points)} points'
        endpoint = cl.points[-1]
        startpoint = cl.pointAlongBy(-d)
        return PolylineRegion([startpoint, endpoint])

    new_cl1 = PolylineRegion.unionAll([tail(r1.predecessor, 10), r1.centerline, r1.successor.centerline])
    new_cl2 = PolylineRegion.unionAll([tail(r2.predecessor, 2), r2.centerline, r2.successor.centerline])

    # Add arrows
    show_arrows(plt, new_cl1, blue, pointsDelts=5, size=1.5)
    show_arrows(plt, new_cl2, red, pointsDelts=5, size=1.5)
    show_cl(plt, new_cl1, blue)
    show_cl(plt, new_cl2, red)
    
    # add objects
    show_object(plt, (113.17, -326.61), math.pi/2, blue)
    show_object(plt, (76.09, -330.57), -math.pi/2, red)


    # save and view
    zoomToIntersection(scene, plt, zoom_margins)
    save_show_clear(plt, f'{dirPath}/fig22.png', view)

    # ###############
    # FIG 3 : Full scenario
    
    # Add regions
    show_reg(plt, r2.predecessor, red)
    show_reg(plt, r2, gray)
    show_reg(plt, r2.successor, blue)
    
    show_network_alt(scene.workspace.network, plt)

    # Add arrows
    show_arrows(plt, full_cl2, white, pointsDelts=5, size=1.5)

    # save and view
    zoomToIntersection(scene, plt, (25, 5, 2, 10))
    save_show_clear(plt, f'{dirPath}/fig3.png', view)

    # ###############
    # FIG 4 : All possible scenarios

    laneregions = {
        93: scene.workspace.network.elements['road93_lane0'],
        94: scene.workspace.network.elements['road94_lane0'],
        102: scene.workspace.network.elements['road102_lane0'],
        103: scene.workspace.network.elements['road103_lane0'],
        108: scene.workspace.network.elements['road108_lane0'],
        109: scene.workspace.network.elements['road109_lane0']
    }

    specifiers = {
        'fig410':(93, -1, -1),
        'fig411':(94, -1, -1),
        'fig412':(102, -1, -1),
        'fig413':(103, -1, -1),
        'fig414':(108, -1, -1),
        'fig415':(109, -1, -1),
        'fig420':(93, 102, -1),
        'fig420':(93, 109, -1),
        'fig421':(93, 103, -1),
        'fig422':(94, 109, -1),
        'fig423':(102, 108, -1),
        'fig424':(108, 102, -1),
        'fig425':(102, 109, -1),
        'fig430':(93, 103, 109),
        'fig431':(109, 93, 94),
        'fig440':(108, 109, 102),
        'fig441':(108, 103, 94)
    }

    colors = (red, blue, blue)

    for figname, spec in specifiers.items():
        for i, laneid in enumerate(spec):
            if laneid == -1:
                continue
            cur_lane = laneregions[laneid]
            show_reg(plt, cur_lane, colors[i])
            show_arrows(plt, cur_lane.centerline, white, pointsDelts=-1, size=1.5)
            if i > 0:
                showPairwiseCollidingRegions([laneregions[spec[0]], cur_lane], plt, gray)
            
        show_network_alt(scene.workspace.network, plt)
        zoomToIntersection(scene, plt, 2)
        save_show_clear(plt, f'{dirPath}/{figname}.png', view)

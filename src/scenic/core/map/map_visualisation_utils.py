
import networkx as nx
import matplotlib.pyplot as plt
from scenic.core.regions import EmptyRegion


def visualizeAbstractGraphs(actor, graphMap, addLabels):

    # Plotting the graph G
    G = graphMap[actor]
    pos = nx.multipartite_layout(G, align='vertical', scale=1)  # Layout algorithm for node positioning
    nx.draw(G, pos, with_labels=False, node_size=1000, font_size=12, node_color='lightblue', edge_color='gray')

    if addLabels:
        labels = {node: f'{node.segmentRegion.uid}\nyassou' for node in G.nodes()}  # Node labels
        nx.draw_networkx_labels(G, pos, labels=labels, font_color='black', font_size=12)

    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='black', font_size=10)

    # Displaying the graph
    plt.title('Graph Title')
    plt.axis('off')
    plt.show()


def showLaneSections(scene, map_plt):
    n = scene.workspace.network

    for rd in n.roads:
        for lane in rd.lanes:
            for laneSec in lane.sections:
                laneSec.show(map_plt, style=':', color='r')


def showPairwiseCollidingRegions(all_roads, map_plt, color='r', zorder=99):
    for i, roadi in enumerate(all_roads[1:2]):
        for roadj in all_roads[:]:
            if roadi == roadj:
                continue
            try:
                collidingRegion = roadi.intersect(roadj)
            except:
                collidingRegion = EmptyRegion('')
            collidingRegion.show(map_plt, style='-', color='w')
            if isinstance(collidingRegion, EmptyRegion):
                continue
            points = tuple(collidingRegion.polygons[0].exterior.coords)
            x, y = zip(*points)
            plt.fill(x, y, color=color, zorder=zorder)


def zoomToIntersection(scene, map_plt, margin=10, id=None):
    if id is not None:
        intersection_id = id
    else:
        intersection_id = scene.params.get('intersectiontesting')
    intersectionsWithId = list(filter(lambda x: x.id == intersection_id, scene.workspace.network.intersections))
    assert len(intersectionsWithId) == 1, f"Invalid intersection id <{intersection_id}>. Select among the following ids {[x.id for x in scene.workspace.network.intersections]}"
    intersection =  intersectionsWithId[0]
    aabb = intersection.getAABB()

    # margins = [xlo, xhi, ylo, yhi]

    if isinstance(margin, int):
        margins = [margin, margin, margin, margin]
    elif isinstance(margin, tuple) and len(margin) == 2:
        margins = [margin[0], margin[0], margin[1], margin[1]]
    elif isinstance(margin, tuple) and len(margin) == 4:
        margins = margin
    else:
        exit(f'Invalid margin <{margin}>. Must be int or tuple of 2 or 4 ints')

    xlo = aabb[0][0]-margins[0]
    xhi = aabb[0][1]+margins[1]
    ylo = aabb[1][0]-margins[2]
    yhi = aabb[1][1]+margins[3]

    fig = map_plt.gcf()
    xrange = xhi-xlo
    yrange = yhi-ylo
    fig.set_size_inches(xrange/2.54, yrange/2.54)  # Convert from centimeters to inches

    map_plt.xlim(xlo, xhi)
    map_plt.ylim(ylo, yhi)
    

def highlightSpecificElement(scene, map_plt):
    uids = [('road1_sec0_lane3', 'c'),
            ('road1_sec1_lane2', 'k'),
            ('road43_lane0', 'k'),
            ('road10_sec0_lane2', 'k')
            ]
    uids = [('road0', 'c'),
            ('road1', 'c'),
            ('road7', 'c')]

    n = scene.workspace.network
    # print(n.elements['road1'].sections)
    loc = n.elements['road1_sec1_lane2']
    print(loc._successor.__repr__())

    print('>>>>>>Depicted<<<<')
    for uid, color in uids:
        elem = n.elements[uid]
        print(elem.__repr__())
        elem.show(map_plt, style='-', color=color, )

def show_alt(scene, zoom=None, dirPath=None, filename='image.png', params=None, block=True, region_to_show=None):
    """Render a schematic of the scene for debugging."""
    
    print(params)
    import matplotlib.pyplot as plt
    fig = plt.figure()
    plt.gca().set_aspect('equal')
    # display map
    scene.workspace.show(plt)
    # draw objects
    for obj in scene.objects:
        obj.show(scene.workspace, plt, highlight=(obj is scene.egoObject))
        # print(scene.workspace.network.nominalDirectionsAt(obj.position))
        # print(obj.heading)

    if region_to_show is not None:
        region_to_show.show(plt, color='k')


    if params.get('view_path'):
        import scenic.core.map.map_backwards_utils as map_utils
        # Below is OLD. for when we were generating vehicles far from the intersection
        # import scenic.core.evol.map_utils as map_utils
        map_utils.handle_paths(scene, params, plt, includeLongPathToIntersection=False)

    # zoom in if requested
    if zoom != None and zoom != 0:
        if scene.params.get('intersectiontesting') != None:
            zoomToIntersection(scene, plt)
        else:
            scene.workspace.zoomAround(plt, scene.objects, expansion=zoom)
    
    if params.get('save_im'):
        filePath = f'{dirPath}/{filename}'
        fig.savefig(filePath)
        print(f'  Saved image at                {filePath}')
    if params.get('view_im'):
        plt.show()

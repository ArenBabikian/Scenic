
import networkx as nx
import matplotlib.pyplot as plt


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


def showPairwiseCollidingRegions(all_roads, map_plt):
    for i, roadi in enumerate(all_roads):
        for roadj in all_roads[i+1:]:
            collidingRegion = roadi.intersect(roadj)
            collidingRegion.show(map_plt, style='-', color='y')


def zoomToIntersection(scene, map_plt):
    margin = 10
    intersection_id = scene.params.get('intersectiontesting')
    intersectionsWithId = list(filter(lambda x: x.id == intersection_id, scene.workspace.network.intersections))
    assert len(intersectionsWithId) == 1, f"Invalid intersection id <{intersection_id}>. Select among the following ids {[x.id for x in scene.workspace.network.intersections]}"
    intersection =  intersectionsWithId[0]
    aabb = intersection.getAABB()

    map_plt.xlim(aabb[0][0]-margin, aabb[0][1]+margin)
    map_plt.ylim(aabb[1][0]-margin, aabb[1][1]+margin)

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
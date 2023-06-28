
from queue import Queue
from scenic.core.evol.heuristics import AbstractSegment, getAbstractPathGraph
from scenic.core.regions import PolygonalRegion

from scenic.domains.driving.roads import Intersection, LaneSection
import networkx as nx
import matplotlib.pyplot as plt

colors = ['#000000',  '#0000EE', '#444444',]

def createAbstractGraph(root_seg: AbstractSegment):
    G = nx.DiGraph()

    q = Queue()
    q.put((root_seg, 0))    
    G.add_node(root_seg, subset = 0)

    while not q.empty():
        cur_seg, dep = q.get()
        for edge_type, child in cur_seg.next_segments.items():
            q.put((child, dep+1))
            G.add_node(child, subset = dep+1)
            G.add_edge(cur_seg, child, label=edge_type)
    return G


def addAbstractPaths(scene, map_plt):
    abstractPathGraphs = {}
    inters_regs = []

    for _, o in enumerate(scene.objects):
    
        root, inters_i_regs = getAbstractPathGraph(o, None)
        
        inters_union = PolygonalRegion.unionAll(inters_i_regs)
        inters_regs.append(inters_union)

        graph = createAbstractGraph(root)
        abstractPathGraphs[o] = graph

    # Show all possible paths of each object
    for k, g in enumerate(abstractPathGraphs.values()):
        combinedRegion = PolygonalRegion.unionAll([x.segmentRegion for x in g.nodes])
        combinedRegion.show(map_plt, style='-', color=colors[k])

    # show pairwise overlapping regions within intersection
    for i in range(len(inters_regs)):
        for j in range(i+1, len(inters_regs)):
            overlap = inters_regs[i].intersect(inters_regs[j])
            overlap.show(map_plt, style='-', color='#7D2E68', )
        
    return abstractPathGraphs


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

# TODO 0 REMOVE THIS, it is only for testing
def _addSegmentHighlighting(scene, plt):
    ws = scene.workspace
    # for o in scene.objects:
    #     allProps = { prop: getattr(o, prop) for prop in o.properties }
    #     allDir = dir(o)
    #     # print(allProps)
    #     with open("output.txt", "w") as f:
    #         # for x in allProps:
    #         #     # print(f'{x}: {getattr(o, x)}')
    #         #     f.write(f'{x}: {getattr(o, x)}\n')
    #         for x in allDir:
    #             # try:
    #             #     f.write(f'<<<{inspect.getsourcefile(getattr(o, x, None))[33:]}>>>\n')
    #             # except:
    #             #     f.write(f'<<<  >>>\n')
    #             try:
    #                 f.write(f'{x}: {getattr(o, x)}\n')
    #             except:
    #                 f.write(f'{x}: ---\n')
    #             # f.write('\n')
    #     exit()


    colors = ['#000000', '#0000D1', '#228B22']
    for j, o in enumerate(scene.objects):
        
        relevant_attributes = {
            'region': o.regionContainedIn,
            '_element': o._element,
            'road': o.road,
            'lane': o.lane,
            'laneGroup': o.laneGroup,
            'laneSection': o.laneSection,
            '_road': o._road,
            '_lane': o._lane,
            '_laneGroup': o._laneGroup,
            '_laneSection': o._laneSection,
            # 'intersection': o.intersection
            # 'polygon':o.polygon
        }
        import pprint
        # pprint.pprint(relevant_attributes)
        # exit()
        # exit()

        def recursive_draw(laneSections):
            all_succ = []
            # if intersection exists


            for i, laneSection in enumerate(laneSections):
                # INTERSECTION
                for laneSection2 in laneSections[i+1:]:
                    inters = laneSection.intersect(laneSection2)
                    if inters:
                        # print(inters)
                        inters.show(plt, style='-', color=colors[j])

                laneSection.show(plt, style='-', color=colors[j])
                # TODO WHAT IF IT IS IN AN INTERSECTION INITIALLY????
                if isinstance(laneSection, LaneSection):
                    lane = laneSection.lane
                else:
                    lane = laneSection
                grp = laneSection.group
                grp_succ = grp.successor
                # print(type(grp_succ))
                if isinstance(grp_succ, Intersection):
                    # print([m.connectingLane for m in filter(lambda x: x.startLane == lane, grp_succ.maneuvers)])
                    succ = [m.connectingLane for m in filter(lambda x: x.startLane == lane, grp_succ.maneuvers)]
                else:
                    succ = [laneSection.successor]

                all_succ.extend(succ)

            return all_succ

        x = [relevant_attributes['laneSection']]
        # print(x.successor)
        # exit()
        for i in range(4):
            # print(i)
            # print(x)
            # for l in x:
            #     print(l.uid)
            x = recursive_draw(x)

        continue

        print(len(relevant_attributes['intersection'].maneuvers))
        for m in relevant_attributes['intersection'].maneuvers:
            m.connectingLane.show(plt, style='-', color='#000000')

        return

        # print(len(ws.network.lanes))
        # exit()

        # for rd in ws.network.connectingRoads:
        for rd in relevant_attributes['intersection'].roads:
            rd.show(plt, style='-', color='#000000')
            print(len(rd.lanes))
        # relevant_attributes['road'].show(plt, style='-', color='#000000')
        # relevant_attributes['intersection'].show(plt, style='-', color='#000000')


# ############################
# GUIDELINES FOR IMPLEMENATION
# ############################

# TODO figure out how I want to segment the straight roads
# maneuver is an intersection maneuver

# DONE    # 0. determine the starting segment of actor

# DONE    # 1 get all possible paths AS A TREE STRUCTURE for actor from a given starting point up (from which we can derive the starting segment) to a certain number of segments
# DONE    # 1.0.0 NOTE CAN WE DO THIS AS AN (assumed NON-CYCLIC) (EDGE-TYPED. each edge has acorrespondiong maneuver attached to it) DIRECTED GRAPH????
    # 1.0.1 CAN WE STORE THE PATHS IN A CACHE FOR EACH SEGMENT AS WE GO?

# DONE # DESIGN DECISION    # 1.1 a path may only contain lane changes in the same direction (a path cant contain a lanechnageR and a laneChangeL), cuz we assume that a lane change is being performed in order to take a specific path in the intersection
# DONE    # 1.2 once an operation of type maneuver (INTERSECTION) has been completed, stop checking for more ath segments

# DONE    # 2.0 For all other actors, do the same thing, except 1.2
# DONE    # The reason we dont wanna pinpoint a collision ara first and guide search accordingly is because the initial position is more dependant on the other initial consraints. we handle the likeliness of collision through this heuristic value

# DONE    # 2.actor for the tree of all possible paths, prune the paths that do not contain a maneuver. This should significantly reduce the tree
# ADDED AS TODO    # 2.other prune paths that never reach an intersection (since we want the collision to happen at the intersection)

    # 3. store in an EXTERNAL cache (as a file that can be loaded, and written to) the {(starting segment, maneuver) : eligible path tree} pair

    # 4. if eligible_actor_paths is empty, <<return heuristic = infinity>> (cuz we never wanna get the ego vehicle in this position, or in the same abstract)

    # ARE THERE COLLISIONS BETWEEN  eligible actor paths, AND a path of at least one other 
    # for each other actor, check if any of their possible paths intersect (collides) with the interesction segments of any of the actor paths

    # get a list of intersecing paths. note that paths are abstract, subtrees. So we get 2 abstractions at the same time:
    # 1. we get th emap abstraction, with the road segments
    # 2. we get an abstract representation of all possible paths as a tree

    # if (for all other actors, none of the possible paths intersect ):
    # <return a very high number as heuristic, or a heuristic based on the closest distance between paths?>

    # collect all abstract abstract paths that are intersecting
    # for each path find the road segment that is part of the collision
    # SO AT THIS POINT, we know that the collision is not impossible

    # Now we evaluate the heuristic value of the paths
    # return a heuristic value based on the difference between the number of steps needed to reach the intersection segment
    # CHALLENGE how can we count the number of needed steps to reach the collision location in the abstract? do lane change steps weigh for more steps?
    # HERE we can most likely do some backwards movement

    # TODO NEXT STEP
    # we can predetermine constrant speeds (multipliers for number of steps) for each 
    # TODO NEXT STEP
    # what do we do with vehicles that are not colliding? can we chose a path that is the closest to the collision spot at collision time?


    # AT THIS POINT, we have a set of possible collision-leading paths for each actor, with a corresponding "time-to-collision" measure. 
    # We can select two paths with the closest time-to-collision, that do not collide anywhere other than intersection.
    # if they do collide somewhere other than the intersection, we can return a high heuristic value

    # So we save the selected pahs somewhere, and MHS returns that as well

    # NOTE heuristic value does not need to be 0 to be acceptable

    # THEEEENNNNN
    # we can highlight the expected paths for each vehicle and we will see the collision.

    # TO SIMULATE
    # we might need to translate the path into a sequence of maneuvers in scenic language for OTHER
    # for eago, we can submit a sequence of road segments




    # once we know that collision can exist, go backwards to find collision-inducing path

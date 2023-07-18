import random
from queue import Queue
from scenic.core.evol.constraints import Cstr_type, Cstr_util
from scenic.core.evol.heuristics import AbstractSegment, getAbstractPathGraph, name2maneuverType
from scenic.core.regions import EmptyRegion, PolygonalRegion

from scenic.domains.driving.roads import Intersection, LaneSection
import networkx as nx
import matplotlib.pyplot as plt

from scenic.formats.opendrive import xodr_parser
from src.scenic.formats.opendrive.xodr_parser import Lane, Poly3

colors = ['#000000',  '#0000EE', '#444444',]

class TwoWaySegment:
    def __init__(self, segment_region):
        self.segment_region = segment_region
        self.prev_segments = set()
        self.next_segments = set()
    
    def add_prev(self, seg):
        self.prev_segments.add(seg)
    def add_next(self, seg):
        self.next_segments.add(seg)

def createAbstractGraph(root_seg: AbstractSegment):
    G = nx.DiGraph()
    twoWayRoot = TwoWaySegment(root_seg.segmentRegion)
    abs2TwoWay = {root_seg:twoWayRoot}

    q = Queue()
    q.put((root_seg, 0))    
    G.add_node(root_seg, subset = 0)

    while not q.empty():
        cur_seg, dep = q.get()
        for edge_type, child in cur_seg.next_segments.items():
            q.put((child, dep+1))

            if child not in abs2TwoWay:
                abs2TwoWay[child] = TwoWaySegment(child.segmentRegion)
            abs2TwoWay[child].add_prev(abs2TwoWay[cur_seg])
            abs2TwoWay[cur_seg].add_next(abs2TwoWay[child])

            G.add_node(child, subset = dep+1)
            G.add_edge(cur_seg, child, label=edge_type)
    return G, abs2TwoWay.values()


def getActorToGraphMap(scene):
    abstractPathGraphs = {}
    actor2twoWay = {}
    actor2nodes = {}
    inters_regs = {}
    for _, o in enumerate(scene.objects):

        root, inters_i_regs = getAbstractPathGraph(o, None)
        print(f'Actor at {o.position} is on segment <{o.laneSection.uid}>')

        inters_regs[o] = inters_i_regs

        graph, twoWayNodes = createAbstractGraph(root)
        actor2twoWay[o] = twoWayNodes
        abstractPathGraphs[o] = graph
        actor2nodes[o] = [x.segmentRegion for x in graph.nodes]

    return abstractPathGraphs, actor2twoWay, actor2nodes, inters_regs


def addAbstractPathsToMap(actor2nodes, actor2intersRegs, style, map_plt):

    # Show all possible paths of each object
    for k, nodes in enumerate(actor2nodes.values()):
        combinedRegion = PolygonalRegion.unionAll(nodes)
        combinedRegion.show(map_plt, style=style, color=colors[k])

    if actor2intersRegs  == None:
        return

    # show pairwise overlapping regions within intersection
    inters_regs = []
    for inters_i_regs in actor2intersRegs.values():
        inters_union = PolygonalRegion.unionAll(inters_i_regs)
        inters_regs.append(inters_union)

    for i in range(len(inters_regs)):
        for j in range(i+1, len(inters_regs)):
            overlap = inters_regs[i].intersect(inters_regs[j])
            overlap.show(map_plt, style=style, color='#7D2E68', )


def getDedicatedPathPerActor(scene, actor2twoWay, actor2intersRegs, collision_cons):

    actor2path = {}
    actor2targetRegion = {}

    actorsMissingPath = [x for x in scene.objects]

    # Find actors that are supposed to collide
    collidingActor2maneuver = {}
    for coll in collision_cons:
        actorX = scene.objects[coll.src]
        maneuver_type = name2maneuverType(coll.tgt)
        collidingActor2maneuver[actorX] = maneuver_type

    for actorA in collidingActor2maneuver:
        if actorA not in actorsMissingPath:
            continue
        actorAIntersRegs = actor2intersRegs[actorA]
        # TODO above, we need to do some filtering for maneuver

        # TODO we get a problem if the map is getting segmented, and we are lookimnmg for the collision but one of the vehicles must go through another intersection before it reaches the colliding intersection

        # FIND THE intersecting (target) regions
        random.shuffle(actorAIntersRegs)
        for actorB in actorsMissingPath:
            if actorB == actorA:
                continue
            actorBIntersRegs = actor2intersRegs[actorB]
            random.shuffle(actorBIntersRegs)

            found_intersection = False
            for intersRegA in actorAIntersRegs:
                for intersRegB in actorBIntersRegs:
                    # if both regions collide, we know the target regions for both actor
                    # we would just need to (1) find the associated TwoWay, 
                    # (2) find the path leading to it, 
                    # (3) return all the nodes in that path

                    try:
                        intersection = intersRegA.intersect(intersRegB)
                    except:
                        intersection = EmptyRegion('')

                    found_intersection =  not isinstance(intersection, EmptyRegion)
                    if found_intersection:
                        # FOUND REGIONS!!
                        actor2targetRegion[actorA] = intersRegA
                        actor2targetRegion[actorB] = intersRegB
                        break
                if found_intersection:
                    break
            if found_intersection:
                break

        # FIND PATHS to target regions
        for actor, intersReg in actor2targetRegion.items():
            actorTwoWays = actor2twoWay[actor]
            intersTwoWays = list(filter(lambda x: x.segment_region == intersReg, actorTwoWays))
            assert len(intersTwoWays) == 1

            # Add the intersecting segment
            actorNodes = [intersReg]
            cur_TwoWay = list(intersTwoWays)[0]

            # Add the next (final) segment
            next_segs = cur_TwoWay.next_segments
            assert len(next_segs) == 1 and len(list(next_segs)[0].next_segments) == 0
            next_seg = list(next_segs)[0].segment_region
            actorNodes.append(next_seg)

            while len(cur_TwoWay.prev_segments) > 0:
                prev_TwoWays = cur_TwoWay.prev_segments
                # TODO we might want to optimize this instead of randomizing (long-temr)
                cur_TwoWay = random.sample(prev_TwoWays, 1)[0]
                actorNodes.append(cur_TwoWay.segment_region)

            # we have assigned paths to actor
            actor2path[actor] = actorNodes
            actorsMissingPath.remove(actor)

    #TODO case where we have a 3rd actor that is not involved in the collision

    return actor2path, {a:[r] for a, r in actor2targetRegion.items()}


# ###################
# MAP HANDLING
# ###################

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


# ###################
# PATH HANDLING
# ###################

def handle_paths(scene, params, map_plt):

    # All reachable segments
    abstractPathGraphs, actor2twoWay, actor2nodes, actor2intersRegs = getActorToGraphMap(scene)

    # dedicated path per actor
    parsed_cons = Cstr_util.parseConfigConstraints(scene.params, 'constraints')
    collision_cons = filter(lambda x: x.type == Cstr_type.COLLIDESATMANEUVER,  parsed_cons)

    actor2path, actor2targetRegion = getDedicatedPathPerActor(scene, actor2twoWay, actor2intersRegs, collision_cons)

    if params['save_path']:
        # TODO
        # Pending what Balazs says is needed
        print
        
    if params['view_path']:

        # Add all reachable nodes
        # addAbstractPathsToMap(actor2nodes, actor2intersRegs, '-', map_plt)
        addAbstractPathsToMap(actor2nodes, None, ':', map_plt)

        # Add dedicated path
        addAbstractPathsToMap(actor2path, actor2targetRegion, '-', map_plt)

        showLaneSections(scene, plt) # TODO will probably  end up as default
        # map_utils.highlightSpecificElement(self, plt, )
        plt.show(block=True) # SHOWS THE FULL MAP # TODO TENTATIVE/TEMPORARY
        # visualizeAbstractGraphs(scene.egoObject, abstractPathGraphs, True)
        return


# ###################
# XODR HANDLING
# ###################

def parse_into_segmments(seg_len, road, next_sec, s, left, right):

    left_segments = {}
    right_segments = {}

    next_seg_s = road.length
    if next_sec is not None:
        next_seg_s = float(next_sec.get('s'))
    cur_section_len = next_seg_s - s

    real_seg_len = -1
    if left is not None:
        left_segments, left_seg_len = parse_lanes_to_segments(left, cur_section_len, seg_len, s)
        real_seg_len = left_seg_len # print(left_segments)

    if right is not None:
        right_segments, right_seg_len = parse_lanes_to_segments(right, cur_section_len, seg_len, s)
        real_seg_len = right_seg_len

    assert left is not None or right is not None

    if right is not None and left is not None:
        assert len(left_segments) == len(right_segments)
        assert right_seg_len == left_seg_len
    left_len = len(left_segments)
    right_len = len(right_segments)
    left_segments_at_i = {}
    right_segments_at_i = {}

    for i in range(max(left_len, right_len)):

        if left_len!= 0:
            left_segments_at_i = left_segments[i]
        if right_len != 0:
            right_segments_at_i = right_segments[i]

        # s of the laneSection is relative to the start of the road
        new_s = (i * real_seg_len) + s
        lane_segment_at_i = xodr_parser.LaneSection(new_s, left_segments_at_i, right_segments_at_i)

        # TODO do linking
        road.lane_secs.append(lane_segment_at_i)


def parse_lanes_to_segments(lanes_elem, cur_section_len, segment_len, s):
        '''Lanes_elem (of a laneSection) should be <left> or <right> element.
        Returns list dict of lane ids and Lane objects.'''

        def getNextOrInf(l, index):
            if index == len(l)-1:
                return float('inf')
            else:
                return l[index+1]

        num_segments = round(cur_section_len/segment_len)
        num_segments = 1 if num_segments == 0 else num_segments
        segment_len_real = cur_section_len/num_segments
    
        lane_segments = [{} for _ in range(num_segments)]
        # [{}] * num_segments # does not work = makes compies of the same {}
        for l in lanes_elem.iter('lane'):
            id_ = int(l.get('id'))
            type_ = l.get('type')
            link = l.find('link')
            pred = None
            succ = None
            if link is not None:
                pred_elem = link.find('predecessor')
                succ_elem = link.find('successor')
                if pred_elem is not None:
                    pred = int(pred_elem.get('id'))
                if succ_elem is not None:
                    succ = int(succ_elem.get('id'))

            widths = list(l.iter('width'))
            offsets = [float(w.get('sOffset')) for w in widths]
            # NOTE: sOffsets are supposed to (1) start from 0 at every laneSection, and (2) be increasing (so the vallue is always relative to the start of the laneSection)

            offset_start_i = 0
            offset_end_i = 0
            for i in range(num_segments):
                
                pred_seg = id_ if i != 0 else pred
                succ_seg = id_ if i != num_segments-1 else succ

                # Create a Lane pbject for each segment
                laneSegment = Lane(id_, type_, pred_seg, succ_seg)

                # Offset handling magic
                seg_start = i * segment_len_real
                seg_end = (i+1) * segment_len_real

                wo_start = offsets[offset_start_i]
                wo_end = getNextOrInf(offsets, offset_end_i)
                if wo_end == seg_start:
                    offset_start_i += 1
                    offset_end_i += 1
                    wo_start = offsets[offset_start_i]
                    wo_end = getNextOrInf(offsets, offset_end_i)

                calc_offsets = [seg_start-wo_start] # relative to the start of the segment
                local_offsets = [0] # relative to the start of the segment
                while seg_end > wo_end:
                    local_offsets.append(wo_end-seg_start)
                    calc_offsets.append(0)
                    offset_end_i += 1
                    wo_end = getNextOrInf(offsets, offset_end_i)

                # Going through list of wdths
                for j in  range(offset_start_i, offset_end_i+1):
                    w = widths[j]
                    o = local_offsets[j-offset_start_i]
                    offset = calc_offsets[j-offset_start_i]

                    a = float(w.get('a'))
                    b = float(w.get('b'))
                    c = float(w.get('c'))
                    d = float(w.get('d'))
                    a_new = a + b*offset + c*offset*offset + d*offset*offset*offset
                    b_new = b + 2*c*offset + 3*d*offset*offset
                    c_new = c + 3*d*offset
                    d_new = d
                    w_poly = Poly3(a_new, b_new, c_new, d_new)
                    laneSegment.width.append((w_poly, o))
                lane_segments[i][id_] = laneSegment
                offset_start_i = offset_end_i

        return lane_segments, segment_len_real


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


from scenic.core.evol.map_utils import addAbstractPathsToMap, showLaneSections, visualizeAbstractGraphs
from scenic.domains.driving.roads import _toVector, Intersection, Lane
import matplotlib.pyplot as plt
import networkx as nx
from queue import Queue

PATHLENGTH = 0 # Adjustable


class AbstractSegment:
    # Abstract road segment, which corresponds to a node in the abstract graph of segments an actor may traverse.
    # each such abstract segment is associated to a single corresponding laneSegment

    def __init__(self, segment_region):
        self.segmentRegion = segment_region
        self.laneChangeToReach = None
        # self.intersection = None

        self.prev_segments = {}

    def addPrevSegment(self, prevAbstractSegment, edgeType:str):
        self.prev_segments[edgeType] = prevAbstractSegment
        
        # DESIGN DECISION: validation to avoid zig-zag paths
        if edgeType == 'lc_right' or edgeType == 'lc_left':
            prevAbstractSegment.laneChangeToReach = edgeType


def createAbstractGraph(root_seg: AbstractSegment):
    G = nx.DiGraph()

    q = Queue()
    q.put((root_seg, 0))    
    G.add_node(root_seg, subset = 0)
    print('Hello')

    while not q.empty():
        print(q.qsize())
        cur_seg, dep = q.get()
        for edge_type, child in cur_seg.prev_segments.items():
            q.put((child, dep+1))

            G.add_node(child, subset = dep+1)
            G.add_edge(cur_seg, child, label=edge_type)
    return G


def getPrevSegments(current_segment: AbstractSegment):

    current_region = current_segment.segmentRegion
    current_group = current_region.group
    current_lane = current_region.lane

    predecessor = current_region._predecessor
    if predecessor == None:
        return []

    group_predecessor = current_group._predecessor

    #for now, we avoid cases where the vehicle must drive through another intersection to reach the target intersection
    if isinstance(group_predecessor, Intersection):
        return []

    # Determine predecessors
    predecessor_pairs = [('straight', predecessor)]
    # NOTE to test the ZIG-ZAG, we can coment out below
    left_lane = predecessor._laneToLeft
    if current_segment.laneChangeToReach != 'lc_right' and left_lane:
        if left_lane.group == predecessor.group:
            predecessor_pairs.append(('lc_left', left_lane))

    right_lane = predecessor._laneToRight
    if current_segment.laneChangeToReach != 'lc_left' and right_lane:
        if right_lane.group == predecessor.group:
            predecessor_pairs.append(('lc_right', right_lane))

    # returns a list of (maneuver_name, target_map_region) pairs, and wether the segments are leafs
    return predecessor_pairs



def createGraphOfPaths(currentRoad, scene):
    
    regId2seg = {}
    currentAbsSeg = AbstractSegment(currentRoad)

    # Handling Next Segment
    # TODO This might be -1 instead of 0 in some cases
    nextRoad = currentRoad._successor.sections[0]
    nextAbsSeg = AbstractSegment(nextRoad)
    nextAbsSeg.addPrevSegment(currentAbsSeg, "straight")

    # Handling Next Segment
    prevRoad = currentRoad._predecessor.sections[-1]
    prevAbsSeg = AbstractSegment(prevRoad)
    currentAbsSeg.addPrevSegment(prevAbsSeg, "straight")

    regId2seg[prevRoad.uid] = prevAbsSeg

    absSegsAtPrevDepth = [prevAbsSeg]
    # return nextAbsSeg

    i = 0
    while i < PATHLENGTH and len(absSegsAtPrevDepth) > 0:
        absSegsAtCurDepth = absSegsAtPrevDepth
        absSegsAtPrevDepth = []

        for cur_segment in absSegsAtCurDepth:
            prev_seg_specs = getPrevSegments(cur_segment)
            for seg_edge_type, prev_reg in prev_seg_specs:

                # Storing in a 'CACHE'
                # IS PROBABLY NOT NECESSARY
                key = prev_reg.uid
                if key in regId2seg:
                    prev_seg = regId2seg[key]
                else:
                    prev_seg = AbstractSegment(prev_reg)
                    regId2seg[key] = prev_seg


                cur_segment.addPrevSegment(prev_seg, seg_edge_type)
                # handling and selection of next segments is done in 'getNextSegments'
                absSegsAtPrevDepth.append(prev_seg)
        i+=1

    return nextAbsSeg


def getPrevAndNext(currentRoad):
    # Handling Next Segment TODO This might be -1 instead of 0 in some cases
    nextRoad = currentRoad._successor.sections[0]

    # Handling Next Segment
    prevRoad = currentRoad._predecessor.sections[-1]

    return [prevRoad, currentRoad, nextRoad]

def findRoadInIntersection(actor, scene):
    pos = _toVector(actor.position)
    heading = actor.heading

    all_man = scene.workspace.network.intersectionAt(pos).maneuvers
    current_connectingRoad = [m.connectingLane for m in all_man if m.connectingLane.orientation[pos] == heading]

    # TODO The line below is potetntially causing a bug...
    assert len(current_connectingRoad) == 1, f'INVALID HEADING FOR {actor} ({len(current_connectingRoad)})'
    return current_connectingRoad[0]


def handle_paths(scene, params, map_plt, includeLongPathToIntersection):
    # We are given moment-before-collision positions and orientations of each actor

    actor2graph = {}
    actor2nodes = {}
    for actor in scene.objects:
        # 1. Determine current connectingRoad of each actor
        currentRoad = findRoadInIntersection(actor, scene)

        if includeLongPathToIntersection:
            # 2. Create Graph of possible paths
            rootAbsSeg = createGraphOfPaths(currentRoad, scene)

            # 3. Create Graph from root Absract Segment
            graph = createAbstractGraph(rootAbsSeg)
            actor2graph[actor] = graph

            # 4. Extract the list of all possible stratingSegments
            actorPath = [x.segmentRegion for x in graph.nodes]
            actor2nodes[actor] = actorPath

            #4. Derive an individual exact path
        else:                
            # 2 Get next road segment (target segment) and previous segment (source segment)
            actorPath = getPrevAndNext(currentRoad)
            actor2nodes[actor] = actorPath

    if params['save_path']:
        # TODO
        # Pending what Balazs says is needed
        print
        
    if params['view_path']:

        # Add all reachable nodes
        addAbstractPathsToMap(actor2nodes, None, '-', map_plt)

        # Add dedicated path (not for now)
        # addAbstractPathsToMap(actor2path, actor2targetRegion, '-', map_plt)

        showLaneSections(scene, plt) # TODO will probably  end up as default
        # map_utils.highlightSpecificElement(self, plt, )
        plt.show(block=True) # SHOWS THE FULL MAP # TODO TENTATIVE/TEMPORARY
        # visualizeAbstractGraphs(scene.egoObject, actor2graph, True)
        exit
        return

    exit()
    return 
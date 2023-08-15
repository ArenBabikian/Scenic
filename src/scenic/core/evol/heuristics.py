
from scenic.core.regions import EmptyRegion, PolygonalRegion, PolylineRegion
from scenic.domains.driving.roads import Intersection, Lane, LaneSection, ManeuverType, _toVector
from queue import Queue
import scenic.core.evol.heuristics_utils as heu_utils

MAXPATHLENGTH = 50
ALLOWEDABSTRACTEDGETYPES = {'rd_straight', 'rd_lc_r', 'rd_lc_l', 'is_left', 'is_right', 'is_straight'}

MANEUVERNAME2TYPE = {
    'is_right': ManeuverType.RIGHT_TURN,
    'is_straight': ManeuverType.STRAIGHT,
    'is_left': ManeuverType.LEFT_TURN,
    'is_any': None
}

MANEUVERTYPE2NAME = {
    ManeuverType.RIGHT_TURN: 'is_right',
    ManeuverType.STRAIGHT: 'is_straight',
    ManeuverType.LEFT_TURN: 'is_left'
}


class AbstractSegment:
    # Abstract road segment, which corresponds to a node in the abstract graph of segments an actor may traverse.
    # each such abstract segment is associated to a single corresponding laneSegment

    def __init__(self, segment_region):
        self.segmentRegion = segment_region
        self.laneChangeToReach = None
        self.intersection = None

        self.isLeaf = False

        self.next_segments = {}

    def addNextSegment(self, nextAbstractSegment, edgeType:str, intersection):
        if edgeType not in ALLOWEDABSTRACTEDGETYPES:
            raise AssertionError(f'{edgeType} abstract edge type is not allowed')
        
        if edgeType in self.next_segments:
            # TODO check this
            assert self.next_segments[edgeType] == nextAbstractSegment
            print("WARNING: potential infinite loop")
            # raise AssertionError(f'{edgeType} abstract edge type already set for {self}')

        # DESIGN DECISION: validation to avoid zig-zag paths
        assert not (self.laneChangeToReach == 'rd_lc_l' and edgeType == 'rd_lc_r')
        assert not (self.laneChangeToReach == 'rd_lc_r' and edgeType == 'rd_lc_l')
        if edgeType == 'rd_lc_r' or edgeType == 'rd_lc_l':
            nextAbstractSegment.laneChangeToReach = edgeType

        self.next_segments[edgeType] = nextAbstractSegment

        if edgeType.startswith('is'):
            nextAbstractSegment.intersection = intersection


def getNextSegments(current_segment: AbstractSegment, target_maneuver: ManeuverType):

    # DESIGN DECISION: we end searching for paths 1 segment after the first intersection 
    if current_segment.isLeaf:
        return [], None, None
    
    nextIsLeaf = False

    # TODO 1 current_region  is a laneSection
    current_region = current_segment.segmentRegion
    if isinstance(current_region, LaneSection):
        lane = current_region.lane
    else:
        lane = current_region

    laneSection_successor = current_region._successor
    if laneSection_successor == None:
        return [], None, None

    # When we are at an intersection, laneSection_successor is a Lane already
    if isinstance(laneSection_successor, Lane):
        lane_successor = laneSection_successor
    else:
        lane_successor = laneSection_successor.lane
    current_group = current_region.group
    group_successor = current_group._successor

    succ_intersection = None

    # Check if successor is in an intersection
    succ_is_intersection = False
    if isinstance(group_successor, Intersection):
        all_conecting_lanes = {m.connectingLane for m in group_successor.maneuvers}
        if lane_successor in all_conecting_lanes:
            # this if is necessary in cases where the has multiple segments, 
            # so the next segment would not be in a intersection, but the next group would be
            succ_is_intersection = True
            succ_intersection = group_successor

    if succ_is_intersection:
        # INTERSECTION QUERIES
        succ_maneuvers = {m for m in filter(lambda x: x.startLane == lane, group_successor.maneuvers)}
        successor_pairs = [(MANEUVERTYPE2NAME[m.type], m.connectingLane) for m in succ_maneuvers]
        # NOTE Cannot do lane change into an intersection
        # NOTE slight semantic thing, ex. we are "right_turning" into the connecting lane. This is to prevent cases where we have multiple rd_straight segments if a segment leads into an intersection 
    
        # TODO 2 in the case where a target maneuver is given, must do taget maneuver at intersection.
        # TODO 3 if taret maneuver not possiple, we prune  all the way back to the segmet that has >1 children
    else:
        # ROAD QUERIES
        successor = current_region._successor
        # validate successor type
        # TODO with the road segmentation, this could be unnesc
        # TODO among the available sections, we need to select the correct successor
        # problem when currnet lane is in an intersection, and next lane has many sections
        if isinstance(successor, Lane):

            successor = successor.sections[0] # sections should be in order
            #validation
            assert successor._predecessor == None

        successor_pairs = [('rd_straight', successor)]

        # DESIGN DECISION: If the current region is in an intersection,
        # actor can only move into the straight segment
        # TODO 4 Ugly implementatin cuz I cant find a way to find if a lane is
        # a connecting lane (part of intersection) from the region object...
        # DESIGN DECISION: we end searching for paths 1 segment after the first intersection 
        # ASSUMPTION: no two intersections that are adjacent
        if current_segment.intersection:
            nextIsLeaf = False

            # determine if current intersection is a leaf
            non_succ_maneuvers = {m for m in filter(lambda x: x.connectingLane != lane, current_segment.intersection.maneuvers)}
            # print(non_succ_maneuvers)
            non_succ_connecting_roads = [m.connectingLane for m in non_succ_maneuvers]

            for cross_rd in non_succ_connecting_roads:
                try:
                    a = current_region.intersect(cross_rd)
                    if not isinstance(a, EmptyRegion):
                        nextIsLeaf = True
                        break 
                except:
                    # this happens when intersect is a line?
                    nextIsLeaf = False

            # NOTE if we want to stop after any intersection, simply set nextIsLeaf = False here
            return successor_pairs, nextIsLeaf, succ_intersection

        # NOTE to test the ZIG-ZAG, we can coment out below
        left_lane = successor._laneToLeft
        if current_segment.laneChangeToReach != 'rd_lc_r' and left_lane:
            if left_lane.group == successor.group:
                successor_pairs.append(('rd_lc_l', left_lane))

        right_lane = successor._laneToRight
        if current_segment.laneChangeToReach != 'rd_lc_l' and right_lane:
            if right_lane.group == successor.group:
                successor_pairs.append(('rd_lc_r', right_lane))

    # returns a list of (maneuver_name, target_map_region) pairs, and wether the segments are leafs
    return successor_pairs, nextIsLeaf, succ_intersection


def getAbstractPathGraph(actor, target_maneuver, scenario=None):

    # TODO make this global?
    regId2seg = {}
    # root_region is the starting segment of an  actor

    # TODO is belo wrelevant?
    if scenario == None:
        root_region = actor.laneSection
    else:            
        root_region = scenario.network.laneSectionAt(actor.position)
        if root_region == None:
            return None, None
    
    # root_region = actor.position.laneSection # IMPORTANT THIS RETURNS A RANDOM VARIABLE
    root_segment = AbstractSegment(root_region)
    regId2seg[root_region.uid] = root_segment

    # DESIGN DECISION: we end searching for paths 1 segment after the first intersection 
    # TODO 2 in the case where a target maneuver is given, must do taget maneuver at intersection.
    # TODO 3.1 if taret maneuver not possiple, we prune  all the way back to the segmet that has >1 children
    # TODO 3.2 is MAXPATHLENGTH is reached, prune also

    absSegsAtNextDepth = [root_segment]
    all_inters_regs = []

    i = 0
    while i < MAXPATHLENGTH and len(absSegsAtNextDepth) > 0:
        absSegsAtCurDepth = absSegsAtNextDepth
        absSegsAtNextDepth = []

        for cur_segment in absSegsAtCurDepth:
            next_seg_specs, nextIsLeaf, isIntersection = getNextSegments(cur_segment, target_maneuver)
            for seg_man_type, next_reg in next_seg_specs:

                # Storing in a 'CACHE'
                key = next_reg.uid
                if key in regId2seg:
                    next_seg = regId2seg[key]
                else:
                    next_seg = AbstractSegment(next_reg)
                    regId2seg[key] = next_seg

                next_seg.isLeaf = nextIsLeaf

                cur_segment.addNextSegment(next_seg, seg_man_type, isIntersection)
                # handling and selection of next segments is done in 'getNextSegments'
                absSegsAtNextDepth.append(next_seg)

                # if nextIsLeaf is true, it means that cur_segment is in an intersection
                if nextIsLeaf:
                    all_inters_regs.append(cur_segment.segmentRegion)
                # print(f'{seg_man_type} >> {next_reg.uid} {next_seg.__hash__()}, ')
        i+=1

    return root_segment, all_inters_regs


def name2maneuverType(maneuverName):
    if maneuverName not in MANEUVERNAME2TYPE:
        raise Exception(f'Unhandled maneuver type <{maneuverName}>')

    return MANEUVERNAME2TYPE[maneuverName]


def heuristic_collidesAtManeuver(actor, maneuver_name, scenario):

    maneuver_type = name2maneuverType(maneuver_name)
    ego_path_root, ego_inters_regs = getAbstractPathGraph(actor, maneuver_type, scenario)
    # find the one intersection lane it is traversing
    # Tentatively, we will take union of all intersection lanes
    if ego_path_root == None:
        return 10 # TODO 4 TENTATIVE

    ego_inters_union = PolygonalRegion.unionAll(ego_inters_regs)

    other_path_roots = []
    for o in scenario.objects:
        if o != scenario.egoObject:
            other_path_root, other_inters_regs = getAbstractPathGraph(o, None, scenario)
            if other_path_root == None:
                return 10 # TODO 4 TENTATIVE
            
            other_inters_union = PolygonalRegion.unionAll(other_inters_regs)

            try:
                intersection_inters_reg = ego_inters_union.intersect(other_inters_union)
            except:
                # TODO 5 Confirm this:
                # this happens when intersect is a line?
                # Maybe look at this for heuristic = 5
                intersection_inters_reg = EmptyRegion('')

            if not isinstance(intersection_inters_reg, EmptyRegion):
                return 0 # TODO 4 TENTATIVE

            other_path_roots.append(other_path_root)


    # TODO 4 heuristic medium val if intersection regions dont collide but in same intersection
    # TODO 5 a posteriori select colliding path from collision point (this is after MHS finishes)
    # TODO 6 what do we wanna do with vehicle that is not involved in the collision?
    # TODO 7 how to prevent collision before intersection

    return 5 # TODO 4 TENTATIVE

##############################################
def heuristic_notOnSameRoad(scenario, vi, vj):
    heu_val = 0
    penalty_val = 10
    road_i = scenario.network.roadAt(vi.position)
    road_j = scenario.network.roadAt(vj.position)

    # TEMP
    # def getSuccessor(road):
    #     return None if road == None else road._successor
    # def getNoneOrUid(road):
    #     return None if road == None else road.uid
    # print(f'{getNoneOrUid(road_i)} -> {getNoneOrUid(getSuccessor(road_i))}')
    # print(f'{getNoneOrUid(road_j)} -> {getNoneOrUid(getSuccessor(road_j))}')
    # print('----------')

    if road_i == None or road_j == None:
        return penalty_val

    isProblem = road_i == road_j or \
        road_i._successor == road_j or \
        road_j._successor == road_i

    if isProblem:
        heu_val = 10
    return heu_val


############################################################
def heuristic_doingManeuver(actor, maneuver_name, scenario):
    actor_pos = actor.position
    maneuver_type = name2maneuverType(maneuver_name)
    assert scenario.testedIntersection is not None, "Must specify which intersection to test on!!!!"

    targetRegion = scenario.maneuverToRegion[maneuver_type]
    assert targetRegion != None, f"Intersection {scenario.testedIntersection} does not allow {maneuver_type}"

    heu_val = heu_utils.dist_center_to_container(actor, targetRegion)

    return heu_val

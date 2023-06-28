
from scenic.core.regions import EmptyRegion, PolygonalRegion, PolylineRegion
from scenic.domains.driving.roads import Intersection, Lane, LaneSection, ManeuverType, NetworkElement
from queue import Queue


MAXPATHLENGTH = 5
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
        self.isInIntersection = False

        self.isLeaf = False

        self.previous_segments = [] # TEMPORARY

        self.next_segments = {}

    def addNextSegment(self, nextAbstractSegment, edgeType:str):
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
            nextAbstractSegment.isInIntersection = True


def getNextSegments(current_segment: AbstractSegment, target_maneuver: ManeuverType):

    # DESIGN DECISION: we end searching for paths 1 segment after the first intersection 
    if current_segment.isLeaf:
        return [], None

    # TODO 1 current_region  is a laneSection
    current_region = current_segment.segmentRegion
    if isinstance(current_region, LaneSection):
        lane = current_region.lane
    else:
        lane = current_region
    grp = current_region.group
    grp_succ = grp.successor

    if isinstance(grp_succ, Intersection):
        # print([m.connectingLane for m in filter(lambda x: x.startLane == lane, grp_succ.maneuvers)])
        successor_pairs = [(MANEUVERTYPE2NAME[m.type], m.connectingLane) for m in filter(lambda x: x.startLane == lane, grp_succ.maneuvers)]
        # NOTE Cannot do lane change into an intersection
        # NOTE slight semantic thing, ex. we are "right_turning" into the connecting lane. This is to prevent cases where we have multiple rd_straight segments if a segment leads into an intersection 
    
        # TODO 2 in the case where a target maneuver is given, must do taget maneuver at intersection.
        # TODO 3 if taret maneuver not possiple, we prune  all the way back to the segmet that has >1 children

    else:
        successor = current_region.successor
        # validate successor type
        # TODO with the road segmentation, this could be unnesc
        if isinstance(successor, Lane):
            assert len(successor.sections) == 1
            successor = successor.sections[0]

        successor_pairs = [('rd_straight', successor)]

        # DESIGN DECISION: If the current region is in an intersection,
        # actor can only move into the straight segment
        # TODO 4 Ugly implementatin cuz I cant find a way to find if a lane is
        # a connecting lane (part of intersection) from the region object...
        # DESIGN DECISION: we end searching for paths 1 segment after the first intersection 
        # ASSUMPTION: no two intersections that are adjacent
        if current_segment.isInIntersection:
            return successor_pairs, True

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
    return successor_pairs, False


def getAbstractPathGraph(actor, target_maneuver, scenario=None):
    # TODO 1 tentatively missing the segmentation of the map
    # In reality, we would like to have an AbstractSegment for each road segment

    # TODO make this global?
    regId2seg = {}
    # root_region is the starting segment of an  actor
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
            next_seg_specs, isLeaf = getNextSegments(cur_segment, target_maneuver)
            for seg_man_type, next_reg in next_seg_specs:

                # Storing in a 'CACHE'
                key = next_reg.uid
                if key in regId2seg:
                    next_seg = regId2seg[key]
                else:
                    next_seg = AbstractSegment(next_reg)
                    regId2seg[key] = next_seg

                next_seg.isLeaf = isLeaf

                cur_segment.addNextSegment(next_seg, seg_man_type)
                # handling and selection of next segments is done in 'getNextSegments'
                absSegsAtNextDepth.append(next_seg)

                # if isLeaf is true, it means that cur_segment is in an intersection
                if isLeaf:
                    all_inters_regs.append(cur_segment.segmentRegion)
                # print(f'{seg_man_type} >> {next_reg.uid} {next_seg.__hash__()}, ')
        i+=1

    return root_segment, all_inters_regs


def name2maneuverType(maneuverName):
    if maneuverName not in MANEUVERNAME2TYPE:
        raise Exception(f'Unhandled maneuver type <{maneuverName}>')

    return MANEUVERNAME2TYPE[maneuverName]


def collidesAtManeuverHeuristic(actor, maneuver_name, scenario):

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
                intersection_inters_reg = EmptyRegion()

            if not isinstance(intersection_inters_reg, EmptyRegion):
                return 0 # TODO 4 TENTATIVE

            other_path_roots.append(other_path_root)


    # TODO 4 heuristic medium val if intersection regions dont collide but in same intersection
    # TODO 5 a posteriori select colliding path from collision point (this is after MHS finishes)
    # TODO 6 what do we wanna do with vehicle that is not involved in the collision?
    # TODO 7 how to prevent collision before ijntersection

    return 5 # TODO 4 TENTATIVE

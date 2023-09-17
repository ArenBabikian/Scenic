

import copy
from scenic.core.distributions import Samplable
from scenic.core.evol.evol_utils import fillSample
from scenic.core.map.map_utils_definitive import find_colliding_region
from scenic.core.lazy_eval import needsLazyEvaluation
from scenic.core.printer.utils_concrete import EGO_DIST_BEFORE_JUNC, savePathXml
from scenic.core.regions import EmptyRegion, PolylineRegion
from scenic.core.scenarios import Scene
from scenic.core.vectors import Vector

import shapely.geometry
import shapely.ops
import shapely.prepared
from scenic.domains.driving.roads import ManeuverType

from scenic.figures.util import mk


THRESHOLD = 1e-10

SPEED_IN_JUNCTION = 3
SPEED_OUT_JUNCTION = 4

MANTYPE2ID = {ManeuverType.LEFT_TURN:'left',
              ManeuverType.RIGHT_TURN:'right',
              ManeuverType.STRAIGHT:'straight'}

def doStaticAnalysis(scenario, dirPath, viewIm, viewPath):

    all_colliding_tuples = []
    all_tuples = []

    global_depth = int(scenario.params.get('static-num-actors'))
    # global_depth = 4
    intersection = scenario.testedIntersection
    
    all_possible_maneuvers = intersection.maneuvers
    # all_possible_lanes = [(m.connectingLane, m.startLane) for m in all_possible_maneuvers]

    print('-----------------------')
    print(f'There are {len(all_possible_maneuvers)} lanes in {intersection.uid}')
    print(f'There are theoretically {len(all_possible_maneuvers) ** global_depth} {global_depth}-tuples.')

    # def recursiveForLoop(lanes, start_id, depth, tuple):
    #     if depth >= 1:
    #         for lane_id, lane in enumerate(lanes[start_id:]):
    #             tuple.append(lane)
    #             recursiveForLoop(lanes, lane_id-depth+global_depth+1, depth - 1, tuple)
    #             tuple.pop()
    #     else:
    #         print(tuple)

    def recursiveForLoop(maneuvers, depth, tuple):
        if depth >= 1:

            for maneuver_id, man in enumerate(maneuvers):
                # lane_pair = (connecting_lane, starting_lane)

                if len(tuple) > 0 and man.connectingLane == tuple[0][0].connectingLane:
                    # CONSTRAINT 1: Non-ego paths must be different than ego path
                    continue
                if len(tuple) > 0 and man.startLane == tuple[0][0].startLane:
                    # CONSTRAINT 2: Non-ego paths must have different starting lane than ego path
                    continue
                if len(tuple) > 1 and tuple[-1][1] >= maneuver_id:
                    # CONSTRAINT 3: All non-ego paths must be distinct (and no permutations)
                    continue 
                # TODO? CONSTRAINT 4: Nonego cars should not be starting on the same road

                tuple.append((man, maneuver_id))
                recursiveForLoop(maneuvers, depth-1, tuple)
                tuple.pop()
        else:
            # Check if ego road is intersecting with ALL non-ego roads
            ego_region = tuple[0][0].connectingLane
            heu_val = 0
            for man, reg_id in tuple[1:]:
                non_ego_region = man.connectingLane

                _, local_heu = find_colliding_region(ego_region, non_ego_region)
                heu_val += local_heu

            if heu_val == 0:
                # all_colliding_tuples.append([(lane_spec[0].connectingLane, lane_spec[0].type) for lane_spec in tuple])
                all_colliding_tuples.append([lane_spec[0] for lane_spec in tuple])
            all_tuples.append([lane_spec[0] for lane_spec in tuple])

    recursiveForLoop(all_possible_maneuvers, global_depth, [])

    print(f'We evaluate {len(all_tuples)} {global_depth}-tuples. {len(all_colliding_tuples)} of them are colliding.')

    ############################
    # GENERATE INITIAL POSITIONS

    for i, colliding_tuple in enumerate(all_colliding_tuples[:]):
        # HERE we have a tuple of colliding paths
        ego_man = colliding_tuple[0]
        ego_reg = ego_man.connectingLane

        # DETERMINE EGO POSITION
        # For now, ego will be placed 5m away from the intersection
        ego_starting_reg = ego_reg._predecessor.sections[-1]

        cl_starting = ego_starting_reg.centerline
        ego_strating_point = cl_starting.pointAlongBy(-EGO_DIST_BEFORE_JUNC)

        # print(cl.length)
        # print(cl.pointAlongBy(-10))
        # print(cl.uniformPointInner())
        # p = Vector(-52.64595333171398,-95.00531088611216)
        # p_n = cl.project(p)
        # print(p)
        # print(p_n)
        # print(cl.distanceTo(p_n))
        # print(cl.containsPoint(p_n))
        # exit()

        setup_actor(scenario.objects[0], ego_strating_point, ego_reg, ego_reg, ego_man.type)
        collision_reg = None

        for other_i, other_man in enumerate(colliding_tuple[1:]):
            # HERE we have a pair of lanes that we are dealing with
            other_reg = other_man.connectingLane

            # Step 1: Find the COLLISION REGION
            collision_reg, _ = find_colliding_region(ego_reg, other_reg)
            assert collision_reg != EmptyRegion('')

            # Step 2 (EGO): Find EGO distances to relevant points (distance is INSIDE junction)
            d_e_entering, d_e_middle, d_e_exitting = find_dist_to_coll_reg(collision_reg, ego_reg)

            # Step 3 (EGO): Find EGO time to the interesting point
            d_e_relevant = d_e_entering # TODO
            # TODO be dynamic in EGO_DIST_BEFORE_JUNC
            t_e_to_relevant = find_time_to_relevant(d_e_relevant, EGO_DIST_BEFORE_JUNC)

            # Step 4 (OTHER): Find OTHER distances to relevant points (distance is INSIDE junction)
            d_o_entering, d_o_middle, d_o_exitting = find_dist_to_coll_reg(collision_reg, other_reg)

            # Step 5 (OTHER): Find OTHER position from required time
            d_o_relevant = d_o_entering # TODO
            other_starting_point, other_starting_reg = find_init_position(t_e_to_relevant, d_o_relevant, other_reg)

            # Step 6 (OTHER): Set up other actor
            setup_actor(scenario.objects[other_i+1], other_starting_point, other_starting_reg, other_reg, other_man.type)

        # CREATE SCENE
        save_dir = mk(dirPath)
        scene = create_dummy_scene(scenario, None)
        
        # SAVE XML
        # savePathXml(scene, f'{save_dir}/paths.xml') # TODO temporarily removed
        savePathXml(scene, f'{save_dir}{i}-paths.xml')
        
        # VISUALISATION
        # save_dir = mk(f'{dirPath}{i}') # TODO temporarily removed
        image_params = {'view_im':viewIm,
                        'view_path':viewPath}
        if image_params['view_im']:
            scene.show(None, None, image_params, True,  collision_reg)


def find_dist_to_coll_reg(collision_reg, actor_lane):
    cl = actor_lane.centerline

    # get centerline in 
    cl_InColl = cl.intersect(collision_reg) # TODO might do an optimizatin by checking through points for first point in the region
    cl_len_inColl = cl_InColl.length

    # get relevant points
    pt_start = cl_InColl.points[0]
    ve_start = Vector(pt_start[0], pt_start[1])
    
    d_coll_middle = cl_len_inColl/2
    pt_middle = cl_InColl.pointAlongBy(cl_len_inColl/2) 
    ve_middle = Vector(pt_middle[0], pt_middle[1])

    d_coll_end = cl_len_inColl
    pt_end = cl_InColl.points[-1]
    ve_end = Vector(pt_end[0], pt_end[1])

    # get centerline outside collision region
    cl_OutColl = cl.difference(collision_reg)
    if isinstance(cl_OutColl.lineString, shapely.geometry.MultiLineString):
        cl_OutColl.lineString = cleanedMultiLineString(cl_OutColl.lineString)
        new_geoms = cl_OutColl.lineString.geoms
        
        assert len(new_geoms) in [1, 2]

        linestring_before_coll = new_geoms[0]
        len_to_CollReg = linestring_before_coll.length
    else:
        # Happens for ego=left, non-ego=straight
        len_to_CollReg = cl_OutColl.length

    # Determine distances
    d_start =  len_to_CollReg
    d_middle = len_to_CollReg+d_coll_middle
    d_end = len_to_CollReg+d_coll_end

    # VALIDATION
    assert cl.pointAlongBy(d_start).distanceTo(ve_start) < THRESHOLD, \
        f'START ISSUE: pointAlong{cl.pointAlongBy(d_start)}, pointComputed{ve_start}, difference:{cl.pointAlongBy(d_start).distanceTo(ve_start)}'
    assert cl.pointAlongBy(d_middle).distanceTo(ve_middle) < THRESHOLD, \
        f'MID ISSUE: pointAlong{cl.pointAlongBy(d_middle)}, pointComputed{ve_middle}, difference:{cl.pointAlongBy(d_middle).distanceTo(ve_middle)}'
    assert cl.pointAlongBy(d_end).distanceTo(ve_end) < THRESHOLD, \
        f'END ISSUE: pointAlong{cl.pointAlongBy(d_end)}, pointComputed{ve_end}, difference:{cl.pointAlongBy(d_end).distanceTo(ve_end)}'

    return d_start, d_middle, d_end


def find_time_to_relevant(d_in, d_out):
    return d_in*SPEED_IN_JUNCTION + d_out*SPEED_OUT_JUNCTION


def find_init_position(t_total, d_in_junction, lane):

    t_for_full_in_junction = d_in_junction*SPEED_IN_JUNCTION
    if t_for_full_in_junction >= t_total:
        # vehicle will start inside the intersection
        d_req_in_junction = t_total / SPEED_IN_JUNCTION
        return lane.centerline.pointAlongBy(d_in_junction-d_req_in_junction), lane
    else:
        # vehicle will start before the intersection
        t_before_junc = t_total-t_for_full_in_junction
        d_before_junc = t_before_junc / SPEED_OUT_JUNCTION

        lane_before_junc = lane._predecessor
        reg_before_junc = lane_before_junc.sections[-1]
        return reg_before_junc.centerline.pointAlongBy(-d_before_junc), lane_before_junc


def cleanedMultiLineString(ls):

    new_mls = ls

    # # CLEAN
    # geoms = ls.geoms
    # segs_to_add = []
    # for g in geoms:
    #     if g.length < THRESHOLD:
    #         continue # Too small

    #     if g.coords[0] == g.coords[-1]:
    #         continue # starts and ends at the smae place

    #     segs_to_add.append(g)

    # new_mls = shapely.geometry.MultiLineString(segs_to_add)

    # UNIFY
    if len(new_mls) > 1:
        all_segs = []

        cur_lane = list(new_mls[0].coords)
        for i_cur, l_cur in enumerate(new_mls[:-1]):
            l_next = new_mls[i_cur + 1]

            cur_last = l_cur.coords[-1]
            next_first = l_next.coords[0]

            if cur_last == next_first:
                cur_lane.extend(l_next.coords[1:])
            else:
                all_segs.append(shapely.geometry.LineString(cur_lane))
                cur_lane = list(l_cur.coords)
        
        all_segs.append(shapely.geometry.LineString(cur_lane))  
        new_mls = shapely.geometry.MultiLineString( all_segs )

    return new_mls


def setup_actor(vi, pos, lane, coll_lane, maneuver_type):
    vec = Vector(pos[0], pos[1])
    head = lane.orientation[pos]

    vi.position = vec
    vi.heading = head
    vi.currentLane = coll_lane
    vi.maneuverType = MANTYPE2ID[maneuver_type]
    return


def create_dummy_scene(scenario, positions):
    found = False
    while not found:
        try:
            sample =Samplable.sampleAll(scenario.dependencies)
            found = True
        except:
            print('failed to sample')

    sampledParams = {}
    for param, value in scenario.params.items():
        sampledValue = sample[value]
        assert not needsLazyEvaluation(sampledValue)
        sampledParams[param] = sampledValue
    
    scene = Scene(scenario.workspace, 
                tuple(sample[obj] for obj in scenario.objects),
                sample[scenario.egoObject],
                sampledParams)
    
    return scene

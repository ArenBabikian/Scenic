

import copy
from scenic.core.distributions import Samplable
from scenic.core.evol.evol_utils import fillSample
from scenic.core.map.map_utils_definitive import find_colliding_region
from scenic.core.lazy_eval import needsLazyEvaluation
from scenic.core.printer.utils_concrete import saveAllScenariosToXml, saveScenarioToXml
from scenic.core.regions import EmptyRegion
from scenic.core.scenarios import Scene
from scenic.core.vectors import Vector

import shapely.geometry
import shapely.ops
import shapely.prepared
from scenic.domains.driving.roads import Intersection, ManeuverType

from scenic.figures.util import mk


THRESHOLD = 1e-10
LANE_WIDTH = 3.5
CAR_LENGTH = 5

ACCEL_TIME = 1
COLLISION_TIME_PENALTY = 10

# timeout
INITIAL_SECONDS_DELAY = 5.0
EGO_DIST_BEFORE_JUNC = 5
SECONDS_GIVEN_PER_METERS = 0.8
EXPECTED_COLLISION_TIME = 4

SPEED_IN_JUNCTION = 3
SPEED_OUT_JUNCTION = 4

TIME_MULTIPLER = 1.5

MANTYPE2ID = {ManeuverType.LEFT_TURN:'left',
              ManeuverType.RIGHT_TURN:'right',
              ManeuverType.STRAIGHT:'straight'}

def doStaticAnalysis(scenario, dirPath, viewIm, viewPath, savePaths):

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

    ######################################
    # GENERATE SCENES + FURTHER VALIDATION

    all_scenes = []
    all_timeouts = []
    for i_sc, colliding_tuple in enumerate(all_colliding_tuples[:]):
        # HERE we have a tuple of colliding paths
        ego_man = colliding_tuple[0]
        ego_reg = ego_man.connectingLane

        # DETERMINE EGO POSITION
        # For now, ego will be placed 5m away from the intersection
        ego_starting_reg = ego_reg._predecessor.sections[-1]

        cl_starting = ego_starting_reg.centerline
        ego_strating_point = cl_starting.pointAlongBy(-EGO_DIST_BEFORE_JUNC)

        setup_actor(scenario.objects[0], ego_strating_point, ego_reg, ego_reg, ego_man.type)

        # INITIAL MEASUREMENTS TO SEE WHICH COLLISION HAPPENS WHEN
        collision_reg = None
        ranked_non_ego_by_dist_for_ego = []
        for other_i, other_man in enumerate(colliding_tuple[1:]):
            # HERE we have a pair of lanes that we are dealing with
            other_reg = other_man.connectingLane

            # Step 1: Find the COLLISION REGION
            collision_reg, _ = find_colliding_region(ego_reg, other_reg)
            assert collision_reg != EmptyRegion('')

            # Step 2 (EGO): Find EGO distances to relevant points (distance is INSIDE junction)
            d_e_en, d_e_mi, d_e_ex = find_dist_to_coll_reg(collision_reg, ego_reg)
            
            # Step 4 (OTHER): Find OTHER distances to relevant points (distance is INSIDE junction)
            d_o_en, d_o_mi, d_o_ex = find_dist_to_coll_reg(collision_reg, other_reg)

            # we include:
            # (1) id of corresponding non_ego vehicle
            # (2) distance for ego from start of intersection to start of collision zone (where it woill wait)
            # (3) distance the non-ego will traverse while ego is waiting
            ranked_non_ego_by_dist_for_ego.append({'id':other_i+1, 'dist_to_for_ego':d_e_en, 'dist_in_for_non':d_o_ex-d_o_mi})

        ranked_non_ego_by_dist_for_ego.sort(key=lambda x:x['dist_to_for_ego'])

        # HANDLE NON-EGO ACTORS
        collision_reg = None
        total_added_time = 0
        for other_i, other_man in enumerate(colliding_tuple[1:]):
            # HERE we have a pair of lanes that we are dealing with
            other_reg = other_man.connectingLane

            # Step 1: Find the COLLISION REGION
            collision_reg, _ = find_colliding_region(ego_reg, other_reg)
            assert collision_reg != EmptyRegion('')

            # Step 2 (EGO): Find EGO distances to relevant points (distance is INSIDE junction)
            # NOTE we select EGO_ENTERING point
            d_e_entering, d_e_middle, d_e_exitting = find_dist_to_coll_reg(collision_reg, ego_reg)

            # Step 3 (EGO): Find EGO time to the interesting point
            d_e_relevant = d_e_entering # TODO
            # TODO be dynamic in EGO_DIST_BEFORE_JUNC
            t_e_to_relevant = find_time_to_relevant(d_e_relevant, EGO_DIST_BEFORE_JUNC)

            # Step 4 (OTHER): Find OTHER distances to relevant points (distance is INSIDE junction)
            d_o_entering, d_o_middle, d_o_exitting = find_dist_to_coll_reg(collision_reg, other_reg)

            # STEP 5 (OTHER): is there another collision for ego on the way to this collision region
            time_to_add = 0
            for i_cur, stats_cur in enumerate(ranked_non_ego_by_dist_for_ego):
                if stats_cur['id'] == other_i+1:
                    # Reached the current collision. Finish handling time_to_add
                    break
                i_next = i_cur+1
                if i_next == len(ranked_non_ego_by_dist_for_ego):
                    # This should never happen. 
                    # TODO This only becomes relevant for timeout calculation
                    exit('Pas Fort Aren')
                    # we have reached the final actor, we must add time for the current non_ego
                    time_to_add += stats_cur['dist_in_for_non'] / SPEED_IN_JUNCTION # time for non-ego to finish maneuver (ego decels during this time)
                    time_to_add += ACCEL_TIME # Accel times
                else:
                    stats_next = ranked_non_ego_by_dist_for_ego[i_next]
                    if stats_next['dist_to_for_ego'] < stats_cur['dist_to_for_ego'] + LANE_WIDTH:
                        # collision regions are almost overlapping. Ego handles this as one possible collision
                        # We only add time for the further vehicle behavior
                        print(f'NOTE:    For Scenario {i_sc}, actors {stats_cur["id"]} and {stats_next["id"]} have overlapping collision regions')
                        break 
                    else:
                        time_to_add += (stats_cur['dist_in_for_non'] + CAR_LENGTH) / SPEED_IN_JUNCTION # time for non-ego to finish maneuver (ego decels during this time)
                        time_to_add += ACCEL_TIME # Accel times

            # time_to_add = 0
            t_e_to_relevant += time_to_add
            total_added_time += time_to_add

            # Step 6 (OTHER): Find OTHER position from required time
            # NOTE we select NON_EGO_MIDDLE point
            d_o_relevant = d_o_middle
            other_starting_point, other_starting_reg = find_init_position(t_e_to_relevant, d_o_relevant, other_reg, intersection)

            # Step 6 (OTHER): Set up other actor
            setup_actor(scenario.objects[other_i+1], other_starting_point, other_starting_reg, other_reg, other_man.type)

        # CREATE SCENE
        save_dir = mk(dirPath)
        scene = create_dummy_scene(scenario, None)
        
        # FURTHER VALIDATION
        positioning_problem = False
        for i_ac, vi in enumerate(scene.objects):
            for j_ac_raw, vj in enumerate(scene.objects[i_ac+1:]):
                j_ac = i_ac+1+j_ac_raw

                # VAL : non-egos should initially not overlap
                if vi.intersects(vj):
                    positioning_problem = True
                    # print(f'WARNING: For Scenario {i_sc}, actors {i_ac} and {j_ac} are initially overlapping.')

                # VAL : are non-ego paths overlapping?
                if i_ac != 0:
                    # avoid checking thiss for ego
                    i_reg = colliding_tuple[i_ac].connectingLane
                    j_reg = colliding_tuple[j_ac].connectingLane
                    ij_coll_reg, _ = find_colliding_region(i_reg, j_reg)
                    if ij_coll_reg != EmptyRegion(''):
                        print(f'WARNING: For Scenario {i_sc}, actors {i_ac} and {j_ac} have overlapping paths.')
        
        # ADD SCENE TO DEFINITIVE LIST
        if not positioning_problem:
            all_scenes.append(scene)

        # HANDLE TIMEOUT
        timeout = calculate_timeout(ego_reg, total_added_time)
        all_timeouts.append(timeout)

    print(f'From these {len(all_colliding_tuples)} colliding tuples, {len(all_scenes)} of them do not have initial-position problems.')

    ###########################################
    # FROM SCENES, GENERATE XMLSs and VISUALISE
    for i_sc, scene in enumerate(all_scenes):

        # SAVE individual XML
        if savePaths:
            saveScenarioToXml(scene, f'{save_dir}{i_sc}-paths.xml', all_timeouts[i_sc])
        
        # VISUALISATION
        # save_dir = mk(f'{dirPath}{i}') # TODO temporarily removed
        image_params = {'view_im':viewIm,
                        'view_path':viewPath}
        if image_params['view_im']:
            scene.show(None, None, image_params, True,  collision_reg)

    # SAVE into ONE XML
    if savePaths:
        saveAllScenariosToXml(all_scenes, f'{save_dir}_all-paths.xml', all_timeouts)


def calculate_timeout(ego_reg, total_added_time):

    # Archive
    # dist_in_junc = ego_reg.centerline.length
    # route_length = EGO_DIST_BEFORE_JUNC+dist_in_junc+EGO_DIST_BEFORE_JUNC
    # timeout = int(SECONDS_GIVEN_PER_METERS * route_length + INITIAL_SECONDS_DELAY)

    dist_in_junc = ego_reg.centerline.length
    given_t_in_junc = TIME_MULTIPLER * dist_in_junc / SPEED_IN_JUNCTION
    dist_out_junction = 2*EGO_DIST_BEFORE_JUNC
    given_t_out_junc = TIME_MULTIPLER * dist_out_junction / SPEED_OUT_JUNCTION
    first_potential_collision = TIME_MULTIPLER * EXPECTED_COLLISION_TIME
    added_for_further_collisions = TIME_MULTIPLER*total_added_time

    return int(INITIAL_SECONDS_DELAY + given_t_in_junc + given_t_out_junc + first_potential_collision + added_for_further_collisions)


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
    return d_in / SPEED_IN_JUNCTION + d_out / SPEED_OUT_JUNCTION


def find_init_position(t_total, d_in_junction, lane, testedIntersection):

    t_for_full_in_junction = d_in_junction / SPEED_IN_JUNCTION
    if t_for_full_in_junction >= t_total:
        # VEHICLE WILL START INIDE THE INTERSECTION
        d_req_in_junction = t_total * SPEED_IN_JUNCTION
        return lane.centerline.pointAlongBy(d_in_junction-d_req_in_junction), lane
    else:
        # VEHICLE WILL START BEFRE THE INTERSECTION
        t_before_junc = t_total-t_for_full_in_junction
        d_before_junc = t_before_junc * SPEED_OUT_JUNCTION

        lane_before_junc = lane._predecessor
        reg_before_junc = lane_before_junc.sections[-1]

        if d_before_junc <= reg_before_junc.centerline.length:
            return reg_before_junc.centerline.pointAlongBy(-d_before_junc), lane_before_junc
        else:
            # VEHICLE NEEDS TO START 2 ELEMENTS BEFORE INTERSECTION
            d_before_before_junc = d_before_junc - reg_before_junc.centerline.length

            if len(lane_before_junc.sections) > 1:
                exit('NOT IMPLEMENTED 1')

            lane_before_before_junc = lane_before_junc._predecessor
            if lane_before_before_junc == None:
                # this means that the before_before is a junction

                road_before_junc = lane_before_junc.road
                road_before_before_junc = road_before_junc._predecessor # this is an intersection
                if road_before_before_junc == testedIntersection:
                    road_before_before_junc = road_before_junc._successor
                assert type(road_before_before_junc) == Intersection

                # find the preceding straight road
                condition = lambda man: man.type == ManeuverType.STRAIGHT and man.endLane == lane_before_junc
                all_before_befores = [m.connectingLane for m in filter(condition, road_before_before_junc.maneuvers)]
                # for m in road_before_before_junc.maneuvers:
                #     print(m)
                assert len(all_before_befores) == 1

                lane_before_before_junc = all_before_befores[0]

            # COMPUTE DISTANCE IN BEFORE BEFORE ELEMENT
            if d_before_before_junc > lane_before_before_junc.centerline.length:
                exit('NOT IMPLEMENTED 2')
            
            real_reg_before_before_junc = lane_before_before_junc.sections[-1]
            return real_reg_before_before_junc.centerline.pointAlongBy(-d_before_before_junc), lane_before_before_junc


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

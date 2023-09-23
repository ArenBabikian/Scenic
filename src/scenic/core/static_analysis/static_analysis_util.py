

import copy
from scenic.core.distributions import Samplable
from scenic.core.evol.evol_utils import fillSample
from scenic.core.map.map_utils_definitive import find_colliding_region
from scenic.core.lazy_eval import needsLazyEvaluation
from scenic.core.printer.utils_abstract import saveJsonAbstractScenario
from scenic.core.printer.utils_concrete import MANTYPE2ID, saveAllScenariosToXml, saveScenarioToXml
from scenic.core.regions import EmptyRegion
from scenic.core.scenarios import Scene
from scenic.core.vectors import Vector

import shapely.geometry
import shapely.ops
import shapely.prepared
from scenic.domains.driving.roads import Intersection, ManeuverType

from scenic.figures.util import mk
from pathlib import Path


THRESHOLD = 1e-10
LANE_WIDTH = 3.5
CAR_LENGTH = 5

ACCEL_TIME = 1 # TODO potentially improve
COLLISION_TIME_PENALTY = 10

# timeout
INITIAL_SECONDS_DELAY = 5.0
EGO_DIST_BEFORE_JUNC = 5
SECONDS_GIVEN_PER_METERS = 0.8
EXPECTED_COLLISION_TIME = 4

SPEED_IN_JUNCTION = 3
SPEED_OUT_JUNCTION = 4

TIME_MULTIPLER = 1.5

def doStaticAnalysis(scenario, dirPath):
    # Handle params
    params = scenario.params
    viewIm = params.get('viewImgs') == 'True'
    viewPath = params.get('showPaths') == 'True'
    savePaths = params.get('savePaths') == 'True'
    saveAbsScenarios = params.get('static-saveAbsScenarios') == 'True'

    # Get started
    all_colliding_tuples = []
    all_tuples = []

    global_depth = len(scenario.objects)
    intersection = scenario.testedIntersection
    
    all_possible_maneuvers = intersection.maneuvers
    # all_possible_lanes = [(m.connectingLane, m.startLane) for m in all_possible_maneuvers]

    # SET UP ABSTRACT SCENARIOS
    abstractScenarioDetails = initializeAbstractScenarioDetails(scenario)

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

                tuple.append((man, maneuver_id))
                recursiveForLoop(maneuvers, depth-1, tuple)
                tuple.pop()
        else:
            # Check if ego road is intersecting with ALL non-ego roads
            ego_region = tuple[0][0].connectingLane
            heu_val = 0
            for man, reg_id in tuple[1:]:
                non_ego_region = man.connectingLane

                _, local_heu = find_colliding_region(ego_region, non_ego_region, handle_centerlines=True)
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

        setup_actor(scenario.objects[0], ego_strating_point, ego_reg, ego_reg, ego_man, None, None)

        # INITIAL MEASUREMENTS TO SEE WHICH COLLISION HAPPENS WHEN
        collision_reg = None
        ranked_non_ego_by_dist_for_ego = []
        for other_i, other_man in enumerate(colliding_tuple[1:]):
            # HERE we have a tuple of lanes that we are dealing with
            other_reg = other_man.connectingLane

            # Step 1: Find the COLLISION REGION
            collision_reg, _ = find_colliding_region(ego_reg, other_reg, handle_centerlines=True)
            assert collision_reg != EmptyRegion('')

            # Step 2 (EGO): Find EGO distances to relevant points (distance is INSIDE junction)
            d_e_en, d_e_mi, d_e_ex = find_dist_to_coll_reg(collision_reg, ego_reg)
            
            # Step 4 (OTHER): Find OTHER distances to relevant points (distance is INSIDE junction)
            d_o_en, d_o_mi, d_o_ex = find_dist_to_coll_reg(collision_reg, other_reg)

            # we include:
            # (1) id of corresponding non_ego vehicle
            # (2) distance for ego from start of intersection to start of collision zone (where it woill wait)
            # (3) distance the non-ego will traverse while ego is waiting
            ranked_non_ego_by_dist_for_ego.append({'id':other_i+1, 'dist_to_for_ego':d_e_en, 'dist_in_for_non':d_o_ex-d_o_mi, 'time_to_add':0})

        ranked_non_ego_by_dist_for_ego.sort(key=lambda x:x['dist_to_for_ego'])

        def calculate_time_for_man(dist_in_collision_region):
            # TODO potentially improve this
            # TODO potentially modify the calculation if collision regions are overlapping
            time_for_prev_man = (dist_in_collision_region + CAR_LENGTH) / SPEED_IN_JUNCTION # time for non-ego to finish maneuver (ego decels during this time)
            return time_for_prev_man + ACCEL_TIME


        # DETERMINE HOW MUCH TIME TO ADD TO ENSURE ALL THE COLLISIONS HAPPEN...
        # ...and that non-egos wont collide with each other, at least not  on the path of ego
        for i_cur, stats_cur in enumerate(ranked_non_ego_by_dist_for_ego):
            if i_cur == 0:
                continue

            i_prev = i_cur-1
            stats_prev = ranked_non_ego_by_dist_for_ego[i_prev]
            prev_time_to_add = stats_prev['time_to_add']

            time_to_add_to_non_ego = calculate_time_for_man(stats_prev['dist_in_for_non'])
            new_time_to_add = prev_time_to_add + time_to_add_to_non_ego
            stats_cur['time_to_add'] = new_time_to_add

        # how much time to add to the ego timeout measurement
        ego_time_to_add = 0
        if len(ranked_non_ego_by_dist_for_ego) >= 1:
            stats_last = ranked_non_ego_by_dist_for_ego[-1]
            last_time_to_add = stats_last['time_to_add']

            time_to_add_for_last_man = calculate_time_for_man(stats_last['dist_in_for_non'])
            ego_time_to_add = last_time_to_add + time_to_add_for_last_man

        # HANDLE NON-EGO ACTORS
        collision_reg = None
        for other_i, other_man in enumerate(colliding_tuple[1:]):
            # HERE we have a non_ego vehicle we are focussing on
            other_reg = other_man.connectingLane

            # Step 1: Find the COLLISION REGION
            collision_reg, _ = find_colliding_region(ego_reg, other_reg, handle_centerlines=True)
            assert collision_reg != EmptyRegion('')

            # Step 2 (EGO): Find EGO distances to relevant points (distance is INSIDE junction)
            # NOTE we select EGO_ENTERING point
            d_e_entering, d_e_middle, d_e_exitting = find_dist_to_coll_reg(collision_reg, ego_reg)

            # Step 3 (EGO): Find EGO time to the interesting point
            d_e_relevant = d_e_entering
            t_e_to_relevant = find_time_to_relevant(d_e_relevant, EGO_DIST_BEFORE_JUNC)

            # NOTE: the non_ego should reach the point_of_interest at the same time as ego reaches the point of interest (i.e. in t_e_to_relevant time) 
            # STEP 4 (OTHER) : find time to add due to other collision regions on the way 
            time_to_add_list = [ stats['time_to_add'] for stats in filter(lambda non_ego_stats: non_ego_stats['id'] == other_i+1, ranked_non_ego_by_dist_for_ego)]
            assert len(time_to_add_list) == 1
            time_to_add_new = time_to_add_list[0] # to consider delays caused by previously occured collisions
            t_o_to_relevant = t_e_to_relevant + time_to_add_new

            # Step 5 (OTHER): Find OTHER distances to relevant points (distance is INSIDE junction)
            d_o_entering, d_o_middle, d_o_exitting = find_dist_to_coll_reg(collision_reg, other_reg)

            # Step 6 (OTHER) : Select relevant point
            # NOTE we select NON_EGO_MIDDLE point, unless NON_EGO is performing a right turn, in which case, we select NON_EGO_EXITTING
            # TODO maybe only do this if ego is going straight?
            d_o_relevant = d_o_exitting if other_man.type == ManeuverType.RIGHT_TURN else d_o_middle

            # Step 7 (OTHER) : Find OTHER position from required time
            other_starting_point, other_starting_reg, other_pre_junc_point, other_pre_junc_reg = find_init_position(t_o_to_relevant, d_o_relevant, other_reg, intersection)

            # Step 7 (OTHER): Set up other actor
            setup_actor(scenario.objects[other_i+1], other_starting_point, other_starting_reg, other_reg, other_man, other_pre_junc_point, other_pre_junc_reg)

        # CREATE SCENE
        if savePaths or saveAbsScenarios:
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
                    print(f'WARNING: SCENARIO {i_sc} VOIDED, actors {i_ac} and {j_ac} are initially overlapping.')

                # VAL : are non-ego paths overlapping?
                if i_ac != 0:
                    # avoid checking thiss for ego
                    i_reg = colliding_tuple[i_ac].connectingLane
                    j_reg = colliding_tuple[j_ac].connectingLane
                    ij_coll_reg, _ = find_colliding_region(i_reg, j_reg, handle_centerlines=True)
                    # if ij_coll_reg != EmptyRegion(''):
                    #     print(f'WARNING: For Scenario {i_sc}, actors {i_ac} and {j_ac} have overlapping paths.')
        
        # ADD SCENE TO DEFINITIVE LIST
        if not positioning_problem:
            all_scenes.append(scene)

        # HANDLE TIMEOUT
        timeout = calculate_timeout(ego_reg, ego_time_to_add)
        all_timeouts.append(timeout)

    print(f'From these {len(all_colliding_tuples)} colliding tuples, {len(all_scenes)} of them do not have initial-position problems.')

    ###########################################
    # FROM SCENES, GENERATE XMLSs and VISUALISE
    for i_sc, scene in enumerate(all_scenes):

        # SAVE individual XML, TEMPORARILY REMOVED
        if savePaths and False:
            saveScenarioToXml(scene, f'{save_dir}{i_sc}-paths.xml', all_timeouts[i_sc])
        
        # VISUALISATION
        image_params = {'view_im':viewIm,
                        'view_path':viewPath}
        if image_params['view_im']:
            scene.show(None, None, image_params, True,  collision_reg)

        # ADD ABSTRACT SCENARIO
        if saveAbsScenarios:
            addSpecifcAbstractScenario(scene, abstractScenarioDetails, i_sc)

    # SAVE into ONE XML
    if savePaths:
        saveAllScenariosToXml(all_scenes, f'{save_dir}_{global_depth}actors-all-paths.xml', all_timeouts)

    # SAVE ABSTRACT SCENARIOS
    if saveAbsScenarios:
        saveJsonAbstractScenario(abstractScenarioDetails, f'{save_dir}_{global_depth}actors-abs-scenarios.json')


def initializeAbstractScenarioDetails(scenario):
    # initializations
    global_depth = len(scenario.objects)
    intersection = scenario.testedIntersection
    all_possible_maneuvers = intersection.maneuvers

        # SET UP ABSTRACT SCENARIOS
    maneuver_ids = [m.connectingLane.uid for m in all_possible_maneuvers]

    MANTYPE2REL = {ManeuverType.LEFT_TURN:'left',
                ManeuverType.RIGHT_TURN:'right',
                ManeuverType.STRAIGHT:'ahead'}

    # define relationships between roads
    road_pair_relations = {}
    for m in all_possible_maneuvers:
        road_pair = (m.startLane.road.uid, m.endLane.road.uid)
        if road_pair not in road_pair_relations:
            road_pair_relations[road_pair] = MANTYPE2REL[m.type]
        else:
            assert road_pair_relations[road_pair] == MANTYPE2REL[m.type]

    # determine relationships between lanes
    def get_relationship_map(lane_collection):
        relationships = {}
        for l1 in lane_collection:
            uid_l1 = l1.uid
            rd_l1 = l1.road.uid
            relationships[uid_l1] = {}
            for l2 in lane_collection:
                uid_l2 = l2.uid
                rd_l2 = l2.road.uid
                lane_pair = (uid_l1, uid_l2)
                if l1 == l2:
                    relation = 'same'
                elif rd_l1 == rd_l2:
                    relation = 'adjacent'
                else:
                    relation = road_pair_relations[(rd_l1, rd_l2)]
                relationships[uid_l1][uid_l2] = relation
                # rela = {'pair':lane_pair, 'relation':relation}
        return relationships

    lane_relationships = get_relationship_map(intersection.incomingLanes)
    lane_relationships.update(get_relationship_map(intersection.outgoingLanes))
    return {'map_name' : Path(scenario.params.get('map')).stem,
                               'junction_id' : intersection.uid,
                               'num_actors' : global_depth,
                               'all_maneuvers' : maneuver_ids,
                               'lane_relationships' : lane_relationships,
                               'all_scenarios' : []
                               }


def addSpecifcAbstractScenario(scene, abstractScenarioDetails, scenario_id):
        scenario_dict = {'scenario_id' : scenario_id,
                            'actors' : [],
                            'initial_relations' : {},
                            'final_relations' : {}}
        # MANEUVERS
        for i_o, o in enumerate(scene.objects):
            m = o.maneuver
            maneuver_desc = {'id' :m.connectingLane.uid,
                                'type':MANTYPE2ID[m.type],
                                'start_lane_id':m.startLane.uid,
                                'end_lane_id':m.endLane.uid
                                }
            actor_spec = {'id' : i_o,
                            'maneuver' : maneuver_desc
                            }
            scenario_dict['actors'].append(actor_spec)

        # RELATIONS
        for i_o1, o1 in enumerate(scene.objects):
            startLane1 = o1.maneuver.startLane.uid
            endLane1 = o1.maneuver.endLane.uid
            scenario_dict['initial_relations'][i_o1] = {}
            scenario_dict['final_relations'][i_o1] = {}
            for i_o2, o2 in enumerate(scene.objects):
                if o1 == o2:
                    continue
                startLane2 = o2.maneuver.startLane.uid
                endLane2 = o2.maneuver.endLane.uid

                start_relation = abstractScenarioDetails['lane_relationships'][startLane1][startLane2]
                scenario_dict['initial_relations'][i_o1][i_o2] = start_relation

                end_relation = abstractScenarioDetails['lane_relationships'][endLane1][endLane2]
                scenario_dict['final_relations'][i_o1][i_o2] = end_relation

        abstractScenarioDetails['all_scenarios'].append(scenario_dict)


def calculate_timeout(ego_reg, t_added_for_collisions):
    # Archive
    # dist_in_junc = ego_reg.centerline.length
    # route_length = EGO_DIST_BEFORE_JUNC+dist_in_junc+EGO_DIST_BEFORE_JUNC
    # timeout = int(SECONDS_GIVEN_PER_METERS * route_length + INITIAL_SECONDS_DELAY)

    dist_in_junc = ego_reg.centerline.length
    t_in_junc = dist_in_junc / SPEED_IN_JUNCTION
    dist_out_junction = 2*EGO_DIST_BEFORE_JUNC
    t_out_junc = dist_out_junction / SPEED_OUT_JUNCTION

    return int(INITIAL_SECONDS_DELAY + TIME_MULTIPLER * (t_in_junc + t_out_junc  + t_added_for_collisions))


def find_dist_to_coll_reg(collision_reg, actor_lane):
    cl = actor_lane.centerline

    # get centerline in 
    cl_InColl = cl.intersect(collision_reg)
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
    '''
    Returns (initial position, initial lane, point before junction (if inital point is in junc), lane before junction (if inital point is in junc)
    '''

    t_for_full_in_junction = d_in_junction / SPEED_IN_JUNCTION
    if t_for_full_in_junction >= t_total:
        # VEHICLE WILL START INIDE THE INTERSECTION
        d_req_in_junction = t_total * SPEED_IN_JUNCTION
        starting_pos = lane.centerline.pointAlongBy(d_in_junction-d_req_in_junction)

        lane_before_junc = lane._predecessor
        reg_before_junc = lane_before_junc.sections[-1]
        pre_junc_pos = reg_before_junc.centerline.pointAlongBy(-1)
        
        return starting_pos, lane, pre_junc_pos, lane_before_junc
    else:
        # VEHICLE WILL START BEFRE THE INTERSECTION
        # TODO do this recursively
        t_before_junc = t_total-t_for_full_in_junction
        d_before_junc = t_before_junc * SPEED_OUT_JUNCTION

        lane_before_junc = lane._predecessor
        reg_before_junc = lane_before_junc.sections[-1]

        if d_before_junc <= reg_before_junc.centerline.length:
            starting_pos = reg_before_junc.centerline.pointAlongBy(-d_before_junc)
            return starting_pos, lane_before_junc, None, None
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
                assert len(all_before_befores) == 1, print(f'found {len(all_before_befores)} lanes')

                lane_before_before_junc = all_before_befores[0]

            # COMPUTE DISTANCE IN BEFORE BEFORE ELEMENT
            if d_before_before_junc > lane_before_before_junc.centerline.length:
                exit('NOT IMPLEMENTED 2')
            
            real_reg_before_before_junc = lane_before_before_junc.sections[-1]
            starting_pos = real_reg_before_before_junc.centerline.pointAlongBy(-d_before_before_junc)
            return starting_pos, lane_before_before_junc, None, None


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


def setup_actor(vi, pos, lane, coll_lane, maneuver, pre_junc_pos, pre_junc_lane):
    vec = Vector(pos[0], pos[1])
    head = lane.orientation[pos]

    vi.position = vec
    vi.heading = head
    vi.currentLane = coll_lane
    vi.maneuver = maneuver
    if pre_junc_pos != None:
        vi.pre_junc_position = Vector(pre_junc_pos[0], pre_junc_pos[1])
        vi.pre_junc_heading = pre_junc_lane.orientation[pre_junc_pos]


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

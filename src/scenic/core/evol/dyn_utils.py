import random
from scenic.core.evol.constraints import Cstr, Cstr_type, Cstr_util
import json
import os

# ABSTRACT CONSTRAINTS
def gatherAbsCons(scene):

    # Gather abstract constraints
    if scene.params.get('sim-extend') == 'True':

        speed_cons = [e for e in Cstr_type if 100 <= e.value <= 109]
        beh_cons = [e for e in Cstr_type if 110 <= e.value <= 119]
        
        dyn_cons = []
        for obj_id, obj in enumerate(scene.objects):

            # A. Randomly add speed constraint
            dyn_cons.append(Cstr(random.choice(speed_cons), obj_id, -1))

            # B. Randomly add behavior constraint
            dyn_cons.append(Cstr(random.choice(beh_cons), obj_id, -1))

            # TODO check validity of beh con (does it have l/r lane?)
            # TODO will ned to use obj

    else:
        # Read dynamic constraints from input file
        dyn_cons = Cstr_util.parseConfigConstraints(scene.params, 'dyn_constraints')

        # print(dyn_cons)
    
    validate_cons(dyn_cons, len(scene.objects))
    return dyn_cons

def validate_cons(cons, num_obj):

    has_con_type = [[False, False] for _ in range(num_obj)]

    try:
        for c in cons:
            #check correct type and target
            assert int(c.type.value/100)==1, f"ERROR: Non-dynamic constraint <{c}>"
            assert c.tgt == -1, f"ERROR: Target must be -1 for <{c}>"

            con_typ_cat_id = int(c.type.value/110)
            ID2CAT={0:"SPEED", 1:"BEHAVIOR"}
            if has_con_type[c.src][con_typ_cat_id]:
                print(f'ERROR: Duplicate dynamic constraint of type {ID2CAT[con_typ_cat_id]} for actor {c.src}')
                exit()
            else:
                has_con_type[c.src][con_typ_cat_id] = True
    except AssertionError as msg:
        print(msg)
        exit()

    all_true = True
    for actor_id, cons_for_obj in enumerate(has_con_type):
        for c in cons_for_obj:
            if not c:
                print(f'ERROR: Missing dynamic constraint of type {ID2CAT[c]} for actor {actor_id}')
                all_true = False

    if not all_true:
        exit()

        

# CONCRETIZATION
def concretizeDynamicAbstractScene(scene, dyn_cons):

    # assumes that dyn_cons has been validated
    speed_cons = [e for e in dyn_cons if 100 <= e.type.value <= 109]
    actor_speeds = [None for _ in scene.objects]
    for c in speed_cons:

        if c.type == Cstr_type.SP_SLOW:
            lb, ub = 10, 25
        if c.type == Cstr_type.SP_MED:
            lb, ub = 45, 70
        if c.type == Cstr_type.SP_FAST:
            lb, ub = 70, 105
        speed = random.randint(lb, ub)
        actor = scene.objects[c.src]
        # actor.speed = speed
        # from scenic.core.vectors import Vector
        # vel = Vector(0, speed).rotatedBy(actor.heading)
        # actor.setVelocity(vel)

        # TODO
        # TODO
        # TODO
        # Can I do setspeed directly here?
        actor_speeds[c.src] = speed

    beh_cons = [e for e in dyn_cons if 110 <= e.type.value <= 119]
    behavior_db = scene.behaviorNamespaces['scenic.domains.driving.behaviors'][1]

    for c in beh_cons:
        actor = scene.objects[c.src]
        
        if c.type == Cstr_type.BE_FOLLOW:
            behavior = behavior_db['FollowLaneBehavior'](target_speed = actor_speeds[c.src]) # set (target_speed = actor_speeds[c.src]
        if c.type == Cstr_type.BE_MERGE_LEFT:
            behavior = behavior_db['LaneChangeBehavior'](-1, False) # set (-1, False, actor_speeds[c.src]
        if c.type == Cstr_type.BE_MERGE_RIGHT:
            behavior = behavior_db['LaneChangeBehavior'](1, False) # set (-1, False, actor_speeds[c.src]
        if c.type == Cstr_type.BE_SLOWDOWN:
            behavior = None # TODO
        if c.type == Cstr_type.BE_SPEEDUP:
            behavior = None # TODO
        actor.behavior = behavior

    return actor_speeds # for stats


########
# SAVING
########
def save_aggregate_file(savePath, scenario, srcPath, cons, results):

    stats_agg = {
                'map':scenario.params.get('map'),
                'num_actors': len(scenario.objects),
                'sourcePath': srcPath,
                'abs_scene': [str(c) for c in cons],
                'results': results
            }
    
    print(f'  Saved AGGREGATE simulation stats at    {savePath}')
    with open(savePath, 'w') as outfile:
        json.dump(stats_agg, outfile, indent=4)
    
def init_agg_res(conc_speeds):
    return {'speeds':conc_speeds,
            'num_attempts':0,
            'num_success':0,
            'num_w_collision':0,
            'num_w_nearmiss':0,
            #   'hasCollision':[],
            #   'hasNearMiss':[]
            }

def update_agg_res(dyn_conc_res, success, sim_stats):
    
    #Extract Relevant Info
    if sim_stats is not None:
        hasCollision = int(sum([sum(k) for k in sim_stats['isInCollision']]) > 0)
    else:
        hasCollision = 0

    # SAVE AGGREGATE STATS
    dyn_conc_res['num_attempts']+=1
    if success:
        dyn_conc_res['num_success']+=1
    # simAggStats['results']['hasCollision'].append(hasCollision) # TODO
    # simAggStats['results']['hasNearMiss'].append(-1) # TODO
    dyn_conc_res['num_w_collision'] += hasCollision
    dyn_conc_res['num_w_nearmiss'] += -1

def save_particular_file(file_path, sim_stats):
    
    dir_path = os.path.dirname(file_path)
    os.makedirs(dir_path, exist_ok=True)
    # SAVE PARTICULAR STATS
    print(f'  Saved PARTICULAR simulation stats at    {file_path}')
    with open(file_path, 'w') as outfile:
        json.dump(sim_stats, outfile, indent=4)


def init_part_stats(num_obj):
    return {'position':[[] for _ in range(num_obj)],
            'speed':[[] for _ in range(num_obj)],
            'isOffroad':[[] for _ in range(num_obj)],
            'isInCollision':[[] for _ in range(num_obj)],
            'distBetween':{f'{i}{j}':[] for i in range(num_obj) for j in range(i+1, num_obj) }}

def update_part_stats(simulation):
    for i, o1 in enumerate(simulation.objects):
        simulation.stats['position'][i].append(tuple(o1.position)) # DONE
        simulation.stats['speed'][i].append(o1.speed) # DONE
        simulation.stats['isOffroad'][i].append(-1) # TDOD is there and OffRoadSensor? maybe LaneInvasionEvent?
        # check for collision at current time
        isInColl = simulation.currentTime in simulation.collsensors[i].get_collision_history()
        # print(len(simulation.collsensors[i].get_collision_history()))
        simulation.stats['isInCollision'][i].append(int(isInColl)) # TODO use CollisionSensor
        for j, o2 in enumerate(simulation.objects[i+1:], start=i+1):
            d = o1.euclidianDist(o2)
            simulation.stats['distBetween'][f'{i}{j}'].append(d)

    

    # # TODO conditional to save stats?
    # for i, o1 in enumerate(self.objects):
    #     isInColl = self.currentTime in self.collsensors[i].get_collision_history()
    #     cts = {'t':self.currentTime,
    #            'p':tuple(o1.position),
    #            's':o1.speed,
    #            'off':-1,
    #            'coll':int(isInColl)
    #            }
    #     self.stats[i].append(cts)
    #     # self.stats['position'][i].append() # DONE
    #     # self.stats['speed'][i].append() # DONE
    #     # self.stats['isOffroad'][i].append(-1) # TDOD is there and OffRoadSensor? maybe LaneInvasionEvent?
    #     # # check for collision at current time
    #     # # print(len(self.collsensors[i].get_collision_history()))
    #     # self.stats['isInCollision'][i].append(int(isInColl)) # TODO use CollisionSensor
    #     # for j, o2 in enumerate(self.objects[i+1:], start=i+1):
    #     #     d = o1.euclidianDist(o2)
    #     #     self.stats['distBetween'][f'{i}{j}'].append(d)

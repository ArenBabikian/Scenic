
from copy import Error
import random
from scenic.core.evol.constraints import Cstr_type
from scenic.simulators.utils.colors import Color
import scenic.core.printer.utils as util



#########################
# EVOL ABSTRACT SCENE
def generateEvolConfig(self, constraints, path):
    filePath = f'{path}/d-evol.scenic'
    with open(filePath, "w") as f:
        f.write(util.getParamMap(self))
        f.write('param constraints = \" \\')

        # Default constraints
        for i in range(len(self.objects)):
            f.write(f'ONROAD : [{i}, -1]; \\\n')
        for i in range(len(self.objects)):
            for j in range(i+1, len(self.objects)):
                f.write(f'NOCOLLISION : [{i}, {j}]; \\\n')

        # Added constraints
        for c in constraints:
            f.write(f'{c} \\\n')
        f.write('\"\n')
        f.write('model scenic.simulators.carla.model\n')
        f.write('\n')

        # Actor initializations
        ind_to_name = util.get_actor_names(self)
        for i in range(len(self.objects)):
            col = self.objects[i].color
            if type(col) is Color:
                col = [col.r, col.g, col.b]
            f.write(f'{ind_to_name[i]} = Car with color{col}\n')

    print(f'  Saved evol config file at     {filePath}')


#########################
# SCENIC VENEER SCENE
def generateVeneerRequireConfig(self, sorted_constraints, path):
    
    # PosRel : Veneer
    # DistRel : Veneer if hasAssociatedPosRel else require
    # canSee : require

    # Represenatability
    # posRel cycles = NO
    # canSee cycles = YES
    # obj w/ multi dependencies = NO

    ### PREP

    # Initialize relevant sets
    removedCstrs = []
    canSeeCstrs, posCstrs, distCstrs = sorted_constraints

    # 1. handle cycles
    cycles = util.findCycles(posCstrs)
    # for x in cycles:
    # 	print(x)

    while cycles:
        # find most common constraint
        most_common = util.most_common_cstr(cycles)
        # print(f'REMOVED: <{most_common}>')

        #remove the most common constraint
        posCstrs.remove(most_common)
        removedCstrs.append(most_common)

        #check if cycles are left
        cycles = util.findCycles(posCstrs)

        # for x in cycles:
        # 	print(x)

    # 2. find ordering
    # print('------REMAINING------')
    # for c in posCstrs:
    # 	print(c)

    ordering = util.find_ordering(posCstrs)
    # print(f'ordering = {ordering}')
    

    # 3. handle objects w/ multiple dependencies
    # print('------MULTI-DEP------')
    for i in range(len(self.objects)):
        deps = list(filter(lambda x : x.tgt == i, posCstrs))
        # print(f'{i} = {deps}')
        if len(deps) > 1:
            numToDel = len(deps) - 1
            for _ in range(numToDel):
                itemToDel = random.choice(deps)
                posCstrs.remove(itemToDel)
                deps.remove(itemToDel)
                removedCstrs.append(itemToDel)


    # print(f'REMOVED ALL = {removedCstrs}')
    
    ### START WRITING FILE
    # At this stage, we have: canSee, posRel, distRel, removed Constraints

    ind_to_name = util.get_actor_names(self)
    filePath = f'{path}/d-sc1.scenic'
    with open(filePath, "w") as f:
        f.write(util.getParamMap(self))

        ### handle REMOVED constraints
        if removedCstrs:
            f.write('# The original abstract scenario is IRREPRESENTIBLE.\n')
            f.write('# Thus we removed these constraints to make it representible\n')
            f.write('param constraints = \" \\\n')
            for c in removedCstrs:
                f.write(f'{c} \\\n')
            f.write('\"\n')

        f.write('model scenic.simulators.carla.model\n')
        f.write('\n')

        ### handle POSITION constraints + possibly DISTANCE

        # initialise the actor
        for i in ordering:
            posDepsOfi = list(filter(lambda x : x.tgt == i, posCstrs))
            if len(posDepsOfi) > 1:
                raise Error('Some kind of cycle error!')

            postext = ""
            # Handle positions
            if len(posDepsOfi) == 1:
                posDep = posDepsOfi[0]
                if posDep.type == Cstr_type.HASTOLEFT:
                    direction = "left of"
                if posDep.type == Cstr_type.HASTORIGHT:
                    direction = "right of"
                if posDep.type == Cstr_type.HASBEHIND:
                    direction = "behind"
                if posDep.type == Cstr_type.HASINFRONT:
                    direction = "ahead of"
                posCstrs.remove(posDep)

                s = posDep.src
                t = i

                # Handle distances (if any)
                distDeps = list(filter(lambda x : (x.src == s and x.tgt == t) or (x.src == t and x.tgt == s), distCstrs))
                if len(distDeps) > 1:
                    raise Error('multiple distance constraints!!!')

                lb, ub = 0, 50
                if len(distDeps) == 1:
                    distDep = distDeps[0]					
                    if distDep.type.value == 8:
                        lb, ub = 0, 10
                    if distDep.type.value == 9:
                        lb, ub = 10, 20
                    if distDep.type.value == 10:
                        lb, ub = 20, 50
                    distCstrs.remove(distDep)

                postext = f'{direction} {ind_to_name[s]} by Range({lb}, {ub}), '

            # assign color
            col = self.objects[i].color
            if type(col) is Color:
                col = [col.r, col.g, col.b]
            f.write(f'{ind_to_name[i]} = Car {postext}with color{col}\n')

        if posCstrs:
            raise Error('Remaining position constraints!!')

        f.write('\n')

        ### handle VISIBILITY constraints
        for c in canSeeCstrs:
            f.write(f'require {ind_to_name[c.src]} can see {ind_to_name[c.tgt]}\n')

        ### handle remaining DISTANCE constraints
        for c in distCstrs:
            src = ind_to_name[c.src]
            tgt = ind_to_name[c.tgt]					
            if c.type.value == 8:
                f.write(f'require (distance from {src} to {tgt}) <= 10 \n')
            if c.type.value == 9:
                f.write(f'require 10 <= (distance from {src} to {tgt}) <= 20 \n')
            if c.type.value == 10:
                f.write(f'require 20 <= (distance from {src} to {tgt}) <= 50 \n')

    print(f'  Saved ven-req config file at  {filePath}')
    return [str(c) for c in removedCstrs]


#########################
# SCENIC REGION SCENE
def generateRegionOnlyConfig(self, allConstraints, path):
    
    # PosRel : Region
    # DistRel : Region
    # canSee : Region

    # Represenatability
    # posRel cycles = NO
    # canSee cycles = NO
    # obj w/ multi dependencies = YES

    ### PREP

    # Initialize relevant sets
    removedCstrs = []
    
    # 1. handle cycles
    
    cycles = util.findCycles(allConstraints)

    while cycles:
        # find most common constraint
        most_common_src, most_common_tgt = util.most_common_pair(cycles)

        #remove the most common constraint
        toRemove = list(filter(lambda x : x.src == most_common_src and x.tgt == most_common_tgt, allConstraints))
        for c in toRemove:
            allConstraints.remove(c)
            removedCstrs.append(c)

        #check if cycles are left
        cycles = util.findCycles(allConstraints)

    # 2. find ordering
    ordering = util.find_ordering(allConstraints)
    
    ### START WRITING FILE
    # At this stage, we have: canSee, posRel, distRel, removed Constraints
    ind_to_name = util.get_actor_names(self)
    filePath = f'{path}/d-sc3.scenic'
    with open(filePath, "w") as f:
        f.write(util.getParamMap(self))

        ### handle REMOVED constraints
        if removedCstrs:
            f.write('# The original abstract scenario is IRREPRESENTIBLE.\n')
            f.write('# Thus we removed these constraints to make it representible\n')
            f.write('param constraints = \" \\\n')
            for c in removedCstrs:
                f.write(f'{c} \\\n')
            f.write('\"\n')

        f.write('model scenic.simulators.carla.model\n')
        f.write('\n')

        ### handle ALL constraints (as regions)

        # initialise the actors
        for i in ordering:
            posDepsOfi = list(filter(lambda x : x.tgt == i, allConstraints))
            reg = ""
            # Handle positions
            for d in posDepsOfi:
                addIntersect = reg
                if addIntersect:
                    reg += ".intersect("

                s_name = ind_to_name[d.src]
                if d.type.value == 3:
                    # CANSEE
                    reg += f'SectorRegion({s_name}, 50, {s_name}.heading, math.radians(22.5))'
                if d.type.value == 4:
                    # HASTOLEFT
                    reg += f'SectorRegion({s_name}, 20, {s_name}.heading+(math.pi/2), math.atan(2.5/2))'
                if d.type.value == 5:
                    # HASTORIGHT
                    reg += f'SectorRegion({s_name}, 20, {s_name}.heading-(math.pi/2), math.atan(2.5/2))'
                if d.type.value == 6:
                    # HASBEHIND
                    reg += f'SectorRegion({s_name}, 50, {s_name}.heading+math.pi, math.atan(2/5))'
                if d.type.value == 7:
                    # HASINFRONT
                    reg += f'SectorRegion({s_name}, 50, {s_name}.heading, math.atan(2/5))'
                if d.type.value == 8:
                    # DISTCLOSE
                    reg += f'CircularRegion({s_name}, 10)'
                if d.type.value == 9:
                    # DISTMED
                    reg += f'CircularRegion({s_name}, 20)'
                    if addIntersect : reg += ")"
                    reg += f'.difference(CircularRegion({s_name}, 10)'
                    if not addIntersect : reg += ")"
                if d.type.value == 10:
                    # DISTFAR
                    reg += f'CircularRegion({s_name}, 50)'
                    if addIntersect : reg += ")"
                    reg += f'.difference(CircularRegion({s_name}, 20)'
                    if not addIntersect : reg += ")"
                allConstraints.remove(d)
                
                if addIntersect:
                    reg += ")"
        
            if reg:
                reg = f'in {reg}, '

            # assign color
            col = self.objects[i].color
            if type(col) is Color:
                col = [col.r, col.g, col.b]
            f.write(f'{ind_to_name[i]} = Car {reg}with color{col}\n')

        if allConstraints:
            raise Error('Remaining constraints!!')

    print(f'  Saved reg-onl config file at  {filePath}')
    return [str(c) for c in removedCstrs]


#########################
# SCENIC REGION-REQUIRE SCENE
def generateRegionRequireConfig(self, sorted_constraints, path):
    
    # PosRel : Region
    # DistRel : require
    # canSee : require

    # Represenatability
    # posRel cycles = NO
    # canSee cycles = YES
    # obj w/ multi dependencies = YES

    ### PREP

    # Initialize relevant sets
    removedCstrs = []
    canSeeCstrs, posCstrs, distCstrs = sorted_constraints

    # 1. handle cycles
    cycles = util.findCycles(posCstrs)

    while cycles:
        # find most common constraint
        most_common = util.most_common_cstr(cycles)

        #remove the most common constraint
        posCstrs.remove(most_common)
        removedCstrs.append(most_common)

        #check if cycles are left
        cycles = util.findCycles(posCstrs)

    # 2. find ordering
    ordering = util.find_ordering(posCstrs)
    
    ### START WRITING FILE
    # At this stage, we have: canSee, posRel, distRel, removed Constraints
    ind_to_name = util.get_actor_names(self)
    filePath = f'{path}/d-sc2.scenic'
    with open(filePath, "w") as f:
        f.write(util.getParamMap(self))

        ### handle REMOVED constraints
        if removedCstrs:
            f.write('# The original abstract scenario is IRREPRESENTIBLE.\n')
            f.write('# Thus we removed these constraints to make it representible\n')
            f.write('param constraints = \" \\\n')
            for c in removedCstrs:
                f.write(f'{c} \\\n')
            f.write('\"\n')

        f.write('model scenic.simulators.carla.model\n')
        f.write('\n')

        ### handle POSITION constraints (as regions)

        # initialise the actors
        for i in ordering:
            posDepsOfi = list(filter(lambda x : x.tgt == i, posCstrs))
            reg = ""

            # Handle positions
            for d in posDepsOfi:
                addIntersect = reg
                if addIntersect:
                    reg += ".intersect("

                s_name = ind_to_name[d.src]
                if d.type.value == 4:
                    # HASTOLEFT
                    reg += f'SectorRegion({s_name}, 20, {s_name}.heading+(math.pi/2), math.atan(2.5/2))'
                if d.type.value == 5:
                    # HASTORIGHT
                    reg += f'SectorRegion({s_name}, 20, {s_name}.heading-(math.pi/2), math.atan(2.5/2))'
                if d.type.value == 6:
                    # HASBEHIND
                    reg += f'SectorRegion({s_name}, 50, {s_name}.heading+math.pi, math.atan(2/5))'
                if d.type.value == 7:
                    # HASINFRONT
                    reg += f'SectorRegion({s_name}, 50, {s_name}.heading, math.atan(2/5))'
                posCstrs.remove(d)
                
                if addIntersect:
                    reg += ")"
        
            if reg:
                reg = f'in {reg}, '

            # assign color
            col = self.objects[i].color
            if type(col) is Color:
                col = [col.r, col.g, col.b]
            f.write(f'{ind_to_name[i]} = Car {reg}with color{col}\n')

        if posCstrs:
            raise Error('Remaining position constraints!!')

        f.write('\n')

        ### handle VISIBILITY constraints
        for c in canSeeCstrs:
            f.write(f'require {ind_to_name[c.src]} can see {ind_to_name[c.tgt]}\n')

        ### handle remaining DISTANCE constraints
        for c in distCstrs:
            src = ind_to_name[c.src]
            tgt = ind_to_name[c.tgt]					
            if c.type.value == 8:
                f.write(f'require (distance from {src} to {tgt}) <= 10 \n')
            if c.type.value == 9:
                f.write(f'require 10 <= (distance from {src} to {tgt}) <= 20 \n')
            if c.type.value == 10:
                f.write(f'require 20 <= (distance from {src} to {tgt}) <= 50 \n')

    print(f'  Saved reg-req config file at  {filePath}')
    return [str(c) for c in removedCstrs]




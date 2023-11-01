import os

###########################
# UTILS

def findCycles(self, deps):

    # TODO improve this! This is embarassing :(

    # BUG : [0, 2] - [2, 0] - [0, 2] - [2, 0]
    max = len(self.objects)
    cycles = []

    if max < 1: return cycles

    for c in list(filter(lambda x : x.src == x.tgt, deps)):
        cycles.append([c]) 

    if max < 2: return cycles
    
    for c1 in deps:
        for c2 in list(filter(lambda x : x.src == c1.tgt and x.tgt == c1.src, deps)):
            cycles.append([c1, c2]) 

    if max < 3: return cycles

    for c1 in deps:
        for c2 in list(filter(lambda x : x.src == c1.tgt, deps)):
            for c3 in list(filter(lambda y : y.src == c2.tgt and y.tgt == c1.src, deps)):
                cycles.append([c1, c2, c3])

    if max < 4: return cycles

    for c1 in deps:
        for c2 in list(filter(lambda w : w.src == c1.tgt, deps)):
            for c3 in list(filter(lambda x : x.src == c2.tgt, deps)):
                for c4 in list(filter(lambda y : y.src == c3.tgt and y.tgt == c1.src, deps)):
                    cycles.append([c1, c2, c3, c4])

    if max < 5: return cycles

    for c1 in deps:
        for c2 in list(filter(lambda w : w.src == c1.tgt, deps)):
            for c3 in list(filter(lambda x : x.src == c2.tgt, deps)):
                for c4 in list(filter(lambda z : z.src == c3.tgt, deps)):
                    for c5 in list(filter(lambda y : y.src == c4.tgt and y.tgt == c1.src, deps)):
                        cycles.append([c1, c2, c3, c4, c5])

    if max < 6: return cycles
    
    for c1 in deps:
        for c2 in list(filter(lambda w : w.src == c1.tgt, deps)):
            for c3 in list(filter(lambda x : x.src == c2.tgt, deps)):
                for c4 in list(filter(lambda z : z.src == c3.tgt, deps)):
                    for c5 in list(filter(lambda v : v.src == c4.tgt, deps)):
                        for c6 in list(filter(lambda y : y.src == c5.tgt and y.tgt == c1.src, deps)):
                            cycles.append([c1, c2, c3, c4, c5, c6])

    if max < 7: return cycles
    
    for c1 in deps:
        for c2 in list(filter(lambda w : w.src == c1.tgt, deps)):
            for c3 in list(filter(lambda x : x.src == c2.tgt, deps)):
                for c4 in list(filter(lambda z : z.src == c3.tgt, deps)):
                    for c5 in list(filter(lambda v : v.src == c4.tgt, deps)):
                        for c6 in list(filter(lambda u : u.src == c5.tgt, deps)):
                            for c7 in list(filter(lambda y : y.src == c6.tgt and y.tgt == c1.src, deps)):
                                cycles.append([c1, c2, c3, c4, c5, c6, c7])

    if max < 8: return cycles

    for c1 in deps:
        for c2 in list(filter(lambda w : w.src == c1.tgt, deps)):
            for c3 in list(filter(lambda x : x.src == c2.tgt, deps)):
                for c4 in list(filter(lambda z : z.src == c3.tgt, deps)):
                    for c5 in list(filter(lambda v : v.src == c4.tgt, deps)):
                        for c6 in list(filter(lambda u : u.src == c5.tgt, deps)):
                            for c7 in list(filter(lambda t : t.src == c6.tgt, deps)):
                                for c8 in list(filter(lambda y : y.src == c7.tgt and y.tgt == c1.src, deps)):
                                    cycles.append([c1, c2, c3, c4, c5, c6, c7, c8])

    if max < 9: return cycles

def most_common_cstr(self, cycles):
    # get a full list of involved constraints, with repetition
    full_list = []
    for x in cycles:
        full_list.extend(x)

    # find most common constraint in the cycles
    return max(set(full_list), key=full_list.count)


def most_common_pair(self, cycles):
    # get a full list of involved constraints, with repetition
    all_pairs = []
    for cyc in cycles:
        for con in cyc:
            all_pairs.append((con.src, con.tgt))

    # find most common constraint in the cycles
    return max(set(all_pairs), key=all_pairs.count)


def find_ordering(self, constraints):
    copyCstrs = constraints.copy()
    toBePlaced = list(range(len(self.objects)))
    ordering = []

    while len(ordering) < len(self.objects):
        for i in toBePlaced:

            #check if depends on anything
            if not list(filter(lambda x : x.tgt == i, copyCstrs)):
                # i depends on nothing (above is empty)
                ordering.append(i)
                toBePlaced.remove(i)
                copyCstrs = list(filter(lambda x : x.src != i, copyCstrs))
                break
    
    return ordering


def get_actor_names(self):
    ego = self.egoObject
    ind_to_name = {}
    for i in range(len(self.objects)):
        o = self.objects[i]
        oName = f'o{i}'
        if o is ego:
            oName = 'ego'
        ind_to_name[i] = oName

    return ind_to_name


def getParamMap(self):
    mapPath = os.path.abspath(self.params['map']).replace('\\', '/')
    return f'param map = localPath(\'{mapPath}\')\n'


def seperateByType(self, constraints):
    canSeeCstrs = []
    posCstrs = []
    distCstrs = []

    # seperate constraints
    # Hard-coded numbers
    for c in constraints:
        if c.type.value == 20:
            # Visibility constraints
            canSeeCstrs.append(c)
        elif c.type.value >= 30 and c.type.value <= 39:
            # Positioning Constraints
            posCstrs.append(c)
        elif c.type.value >= 40 and c.type.value < 50:
            # Distance Constraints
            distCstrs.append(c)
        else:
            print(c.type)
            print(c.type.value)
            exit('incorrect constraint type')

    return [canSeeCstrs, posCstrs, distCstrs]
    
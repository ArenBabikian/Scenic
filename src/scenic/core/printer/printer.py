

import copy
import json
from scenic.core.evol.constraints import Cstr, Cstr_type
import scenic.core.printer.utils_concrete as printer_con
import scenic.core.printer.utils_abstract as printer_abs
import scenic.core.printer.utils as util

# MAIN FUNCTION

def printToFile(scene, save_exact, save_abs, path=None, jsonpath='', jsonstats={}):
    if save_exact:
        printer_con.saveExactCoords(scene, path)
    if save_abs is not None:
        stats, cstrs = getAbsScene(scene)
        saveAbsScene(scene, cstrs, stats, save_abs, path, jsonpath, jsonstats)


def getAbsScene(scene):
    stats = {}
    all_heur = {}
    accepted_cstrs = []
    # NOTE: ignoring bidirectional relations
    for i in range(len(scene.objects)):
        oi = scene.objects[i]
        # for j in range(i+1, len(scene.objects)):
        for j in range(len(scene.objects)):
            if i == j:
                continue

            # BIDIRECTIONAL
            oj = scene.objects[j]
            cur_heur = {}

            # POSITION CSTRS
            if oi.toLeftHeuristic(oj) == 0:
                con_type = Cstr_type['HASTOLEFT']
                accepted_cstrs.append(Cstr(con_type, i, j))
            if oi.toRightHeuristic(oj) == 0:
                con_type = Cstr_type['HASTORIGHT']
                accepted_cstrs.append(Cstr(con_type, i, j))
            if oi.inFrontHeuristic(oj) == 0:
                con_type = Cstr_type['HASINFRONT']
                accepted_cstrs.append(Cstr(con_type, i, j))
            if oi.behindHeuristic(oj) == 0:
                con_type = Cstr_type['HASBEHIND']
                accepted_cstrs.append(Cstr(con_type, i, j))

            # CANSEE CSTRS
            val_canSee = oi.canSeeHeuristic(oj)
            cur_heur['CANSEE-A'] = val_canSee
            if val_canSee == 0:
                accepted_cstrs.append(Cstr(Cstr_type['CANSEE'], i, j))

            # UNIDIRECTIONAL
            # only consider distance once, because it is symetric
            if i < j:
                continue

            # DISTANCE CSTRS
            val_close = oi.distCloseHeuristic(oj)
            val_med = oi.distMedHeuristic(oj)
            val_far = oi.distFarHeuristic(oj)
            cur_heur['DISTCLOSE'] = val_close
            cur_heur['DISTMED'] = val_med
            cur_heur['DISTFAR'] = val_far

            # Below is mathematical obligation
            vals_dist = [val_close, val_med, val_far]
            kw = ['DISTCLOSE', 'DISTMED', 'DISTFAR']
            con_type = Cstr_type[kw[vals_dist.index(0)]]
            accepted_cstrs.append(Cstr(con_type, i, j))

            # Add to all heuristics
            ind = (i, j)
            all_heur[ind] = cur_heur

    # sort constraints wrt. type
    accepted_cstrs.sort(key=lambda x: x.type.value)
    n_obj = len(scene.objects)
    n_hard_cons = n_obj + (n_obj * (n_obj-1))/2 #onroad + nocollisions
    stats['num_cons'] = n_hard_cons + len(accepted_cstrs)
    stats['num_hard_cons'] = n_hard_cons
    stats['num_soft_cons'] = len(accepted_cstrs)
    stats['all'] = [str(c) for c in accepted_cstrs]

    return stats, accepted_cstrs


def saveAbsScene(scene, accepted_cstrs, stats, save_spec, path=None, jsonpath='', jsonstats={}):

    # NSGA : includes all constraints (full repr of abs scen)
    if save_spec == 'all' or save_spec == 'evol':
        printer_abs.generateEvolConfig(scene, accepted_cstrs, path)

    # Scenic : some things are not representible
    if save_spec == 'all' or save_spec == 'scenic':
        sorted_cstrs = util.seperateByType(scene, accepted_cstrs)
        del_sc1 = printer_abs.generateVeneerRequireConfig(scene, copy.deepcopy(sorted_cstrs), path)
        stats['deleted-sc1'] = del_sc1
        del_sc2 = printer_abs.generateRegionRequireConfig(scene, copy.deepcopy(sorted_cstrs), path)
        stats['deleted-sc2'] = del_sc2
        del_sc3 = printer_abs.generateRegionOnlyConfig(scene, copy.deepcopy(accepted_cstrs), path)
        stats['deleted-sc3'] = del_sc3

    # Print stats to json
    jsonstats[path] = stats
    print(f'  Saved json stats at           {jsonpath}')
    with open(jsonpath, 'w') as outfile:
        json.dump(jsonstats, outfile, indent=4)

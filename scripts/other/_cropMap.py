import xml.dom.minidom
from xml.dom.minidom import Node
import argparse

m = "zalaFull"
p = f'alt/{m}'

def main():

    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='print details')
    args = argparser.parse_args()

    ver = args.verbose

    # BEGIN
    doc = xml.dom.minidom.parse(f'maps/{p}.xodr')
    roads = doc.getElementsByTagName("road")
    junctions = doc.getElementsByTagName("junction")

    # ROAD and JUNCTIONS o KEEP or to REMOVE
    roads_to_rm = [2541, 3356, 2540]
    # 2541 causing issues (bottom, horizontal road)
    # 8863 causing issues (mid/top right, crescent area) (FIXED at parser-level)
    # 3356 is bottom left
    # 2540 is bottom right

    # connection roads and incoming roads of junctions to keep
    roads_to_keep = [11371, 11383, 11398, 11401, 11416, 11431, 11440, 11443, 11446, 11449, 11452, 11455, 11458, 11461, 11464, 11467, 11470, 11476, 11485, 11488, 11491, 11494, 11497, 11527, 11542, 11545, 11548, 11551, 11554, 11557, 11560, 11563, 11566, 11569, 11572, 11575, 11578]

    juncs_to_keep = [-1, 28, 29, 30, 31, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 55, 57, 58, 59, 60, 61, 62, 63, 64, 68, 69, 70, 71, 72, 73, 54, 56]
    # for the path to big section: 65, 66, 67, 74, 75, 76
    # problems: 27, 32 for 2541 | 54, 56 for 8863
    # for the rest of the map: 0 to 26

    # DELETION CONDITIONS
    # Below is customized for ZalaZone
    del_cond_rd = (lambda r: (r < 2539 or r > 11368 or r in roads_to_rm) and r not in roads_to_keep)
    del_cond_jc = (lambda j: j not in juncs_to_keep)

    # Opposite condition, for testing
    # del_cond_rd = (lambda r:  not ((r < 2539 or r > 11368) and r not in roads_to_keep) or r in roads_to_rm)

    # BEGIN CROPPING
    signal_ids_to_rm = set()
    for r in roads:
        road_id = eval(r.getAttribute("id"))
        junc_id = eval(r.getAttribute("junction"))

        if del_cond_rd(road_id) or del_cond_jc(junc_id):
            # get signals section (should be only one)
            signal_secs = r.getElementsByTagName("signals")
            for signal_sec in signal_secs:
                
                signals = signal_sec.getElementsByTagName("signal")
                for signal in signals:
                    id = signal.getAttribute("id")
                    signal_ids_to_rm.add(id)

            # rm from doc
            r.parentNode.removeChild(r)
            if ver:
                print(f'Removed road {road_id}')
                if not del_cond_rd(road_id):
                    print('DELETED DUE TO JUNCTION CONDITION')
        else:
            # Road is kept
            # remove links to removed roads
            link_secs = r.getElementsByTagName("link")
            for link_sec in link_secs[:1]:
                
                links = list(filter(lambda n: n.nodeType == Node.ELEMENT_NODE, link_sec.childNodes))
                for link in links:
                    # delete link entry if linked to a deleted road
                    ty = link.getAttribute("elementType")
                    id = eval(link.getAttribute("elementId"))
                    if (ty == "road" and del_cond_rd(id)) or (ty == "junction" and del_cond_jc(id)):
                        if ver:
                            print(f'Deleting reference to {ty} {id} in {road_id}')
                        link.parentNode.removeChild(link)

    connecting_roads = set()
    junc_linked_to_kept_rd = set()
    for j in junctions:
        junc_id = eval(j.getAttribute("id"))

        if del_cond_jc(junc_id):
            # rm from doc
            j.parentNode.removeChild(j)
            if ver:
                print(f'Removed junction {junc_id}')

            # but is it linked to a kept road?
            connections = j.getElementsByTagName("connection")
            for connection in connections:
                inc_rd = eval(connection.getAttribute("incomingRoad"))
                con_rd = eval(connection.getAttribute("connectingRoad"))
                if not del_cond_rd(inc_rd) or not del_cond_rd(con_rd):
                    junc_linked_to_kept_rd.add(junc_id)

        else:
            # Junction kept
            # Look at connecting and incoming roads
            connections = j.getElementsByTagName("connection")
            for connection in connections:
                con_rd = eval(connection.getAttribute("connectingRoad"))
                connecting_roads.add(con_rd)
                inc_rd = eval(connection.getAttribute("incomingRoad"))
                connecting_roads.add(inc_rd)

    # Print intersting details
    if ver:
        l_con_roads = list(filter(lambda r: del_cond_rd(r), list(connecting_roads)))
        l_con_roads.sort()
        print('Roads connected to kept junctions.')
        print(l_con_roads)
        print('Junctions connected to kept roads.')
        print(junc_linked_to_kept_rd)

    # HANDLE SINGALS
    # check if signals are referencedin any of the junctions
    for r in roads:
        # get signals section (should be only one)
        signal_secs = r.getElementsByTagName("signals")
        for signal_sec in signal_secs:
            
            signal_refs = signal_sec.getElementsByTagName("signalReference")
            for signal_ref in signal_refs:
                id = signal_ref.getAttribute("id")
                if id in signal_ids_to_rm:
                    signal_ref.parentNode.removeChild(signal_ref)

    # PRINT TO FILE
    pretty = doc.toxml()
    with open(f'maps/{m}crop.xodr', "w") as file1:
        file1.write(pretty)

    print(f'Finished cropping. Saved at maps/{m}crop.xodr')

if __name__ == '__main__':
    main()
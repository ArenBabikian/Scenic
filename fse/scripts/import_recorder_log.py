
import argparse
import os
import carla

def main():
    parser = argparse.ArgumentParser(description='Script to handle --logdir command line argument.')
    parser.add_argument('--replay', help='Replay on simulator', action='store_true', )
    parser.add_argument('--savepath', type=str, help='Save path for save', )
    parser.add_argument('logpath', help='log file to handle', metavar='FILE')
    args = parser.parse_args()

    f = args.logpath
    # Validation
    exit(f"The file '{f}' does not exist.") if not os.path.exists(f) else None
    exit(f"'{f}' is not a file.") if not os.path.isfile(f) else None

    client = carla.Client("172.30.208.1", 2000, worker_threads=1)
    client.set_timeout(5.0)

    filepath = args.logpath
    # print(os.path.exists(filepath))
    # print(os.path.exists('/home/aren/git/Scenic/fse/data-sim/log/0919-231039/RouteScenario_scen_Town05_2240_1ac_0_rep0.log'))
 
    # filepath = "\\\\wsl.localhost\\Ubuntu-18.04\\home\\aren\\git\\Scenic\\fse\\data-sim\\log\\0919-231039\\RouteScenario_scen_Town05_2240_1ac_0_rep0"
    filepath = "\\\\wsl.localhost\\Ubuntu-18.04\\mnt\\c\\git\\carla\\fse\\data-sim\\log\\0919-231039\\RouteScenario_scen_Town05_2240_1ac_0_rep0.log"
    # fse\data-sim\log\0919-231039\RouteScenario_scen_Town05_2240_1ac_0_rep6.log
    # fse/data-sim/log/0919-231039/RouteScenario_scen_Town05_2240_1ac_0_rep0.log

    exit(f"The save file '{filepath}' does not exist.") if not os.path.exists(filepath) else None
    # filepath = "\\\\wsl.localhost\\Ubuntu-18.04\\init"

    log= client.show_recorder_file_info(filepath, True)

    # exit()

    if args.replay:
        # Delete existing actors
        actor_list = client.get_world().get_actors().filter('vehicle.*')
        for actor in actor_list:
            print(actor)
            actor.destroy()

        # Run the simulation
        x = client.replay_file(filepath, 0, 0, 0, 1)
        print(x)

    if args.savepath:
        # savepath = f'{os.path.splitext(args.savepath)[0]}.txt'
        savepath = args.savepath
        with open(savepath, 'w') as f:
            f.write(log)
        print(f'saved log file to {args.savepath}')
    else:
        print(log)

    exit()

    # print(client.show_recorder_collisions(filepath, 'aa', 'aa'))

    



if __name__ == '__main__':
    main()

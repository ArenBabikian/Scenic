param map = localPath('../maps/CARLA/Town02.xodr')
model scenic.simulators.carla.model

#possible_ego_roads = [item for item in network.roads if item.id == 7]
#r_ego = possible_ego_roads[0]
#ego = Car with color[188/256, 185/256, 183/256] # Silver
#a = Car right of ego

ego = Car at -11.31489524 @ -184.73699369
a = Car at -6.31487594 @ -165.55344661, with requireVisible True
#actor_366590980 = Car at 23.76055086 @ -251.22073748, with requireVisible True



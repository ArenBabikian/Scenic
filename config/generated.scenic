param map = localPath('../maps/CARLA/Town02.xodr')
model scenic.simulators.carla.model

# Get road for ego
possible_ego_roads = [item for item in network.roads if item.id == 7]

r_ego = possible_ego_roads[0]

l_ego = Uniform(*r_ego.lanes)
p_ego = OrientedPoint in l_ego.centerline 

# place ego on road

ego = Car at p_ego, with color[188/256, 185/256, 183/256] # Silver


# Get road for other actor 366590980
possible_366590980_roads = [item for item in network.roads if item.id == 7]

r_366590980 = possible_366590980_roads[0]

# place 366590980 on road

p_366590980 = OrientedPoint left of p_ego by Range(0, 5)


actor_366590980 = Car at p_366590980
require (actor_366590980 in r_366590980)




param map = localPath('../maps/CARLA/Town10HD.xodr')
model scenic.domains.driving.model

# Get road with ID 1
roads_with_id_1 = [item for item in network.roads if item.id == 1]
r1 = roads_with_id_1[0]
l1 = Uniform(*r1.lanes)
p1 = OrientedPoint in r1

# Place ego on road 1
ego = Car at p1

param map = localPath('../maps/CARLA/Town02.xodr')
param carla_map = 'Town02'
param maxSteps = 5
# param render = 0
model scenic.simulators.carla.model

# Get road with ID 1
roads_with_id_1 = [item for item in network.roads if item.id == 1]
r1 = roads_with_id_1[0]
l1 = Uniform(*r1.lanes)
pc1 = OrientedPoint in l1.centerline
p1 = OrientedPoint in r1

# Get road with ID 16
roads_with_id_16 = [item for item in network.roads if item.id == 16]
r16 = roads_with_id_16[0]
l16 = Uniform(*r16.lanes)
pc16 = OrientedPoint in l16.centerline
p16 = OrientedPoint in r16

# Place ego on road 1
ego = Car at pc1, with color[188/256, 185/256, 183/256] # Silver

# Define a point that is "left of" and "in front of" p1
# << TODO guess the ranges below >>
pSec = OrientedPoint following roadDirection from pc1 for Range(5, 10)
secondCar = Car at pSec, with color [194/256, 92/256, 85/256] # red


# # pSec2 = OrientedPoint ahead of pc1 by Range(15, 20)
# # # pSec = OrientedPoint at p1 offset  by Range(-5, 0) @ Range(0, 10)

# # # Place the second car at pSec
# # thirdCar = Car at pSec2, with color [75/256, 119/256, 157/256] # blue

# pSide = OrientedPoint ahead of pc1 by Range(15, 20)
# sideCar = Car at pSide, with color [68/256, 160/256, 135/256] # green

# left = OrientedPoint left of pSide by Range(2, 5)

# require (distance from sideCar to left) < 2



# pfarSide = OrientedPoint left of pc1 by Range(0, 5)
# farSideCar2 = Car at pfarSide, with color [75/256, 119/256, 157/256] # blue

# Define the minimum distance between actors
# << TODO guess the number below >>
# require (distance to secondCar) > 5

# Enforce that the second car is in road 16
# require (secondCar in r16)



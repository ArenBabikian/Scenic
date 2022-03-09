
param map = localPath('../maps/CARLA/Town10HD.xodr')

model scenic.domains.driving.model

ego = Car

Pedestrian on visible ego.oppositeLaneGroup.sidewalk

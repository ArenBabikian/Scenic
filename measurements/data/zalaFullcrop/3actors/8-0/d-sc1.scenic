param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASTOLEFT : [2, 0]; \
"
model scenic.simulators.carla.model

ego = Car with color[0.734375, 0.72265625, 0.71484375]
o1 = Car with color[0.7578125, 0.359375, 0.33203125]
o2 = Car right of ego by Range(0, 10), with color[0.29296875, 0.46484375, 0.61328125]

require ego can see o1
require o1 can see ego
require o1 can see o2
require o2 can see ego
require o2 can see o1
require 20 <= (distance from o1 to ego) <= 50 
require 20 <= (distance from o2 to o1) <= 50 

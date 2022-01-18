param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASTOLEFT : [0, 1]; \
HASBEHIND : [2, 0]; \
"
model scenic.simulators.carla.model

o1 = Car with color[0.7578125, 0.359375, 0.33203125]
ego = Car left of o1 by Range(0, 10), with color[0.734375, 0.72265625, 0.71484375]
o2 = Car ahead of ego by Range(10, 20), with color[0.29296875, 0.46484375, 0.61328125]

require ego can see o2
require 20 <= (distance from o2 to o1) <= 50 

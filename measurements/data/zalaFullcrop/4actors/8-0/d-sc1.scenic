param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASTOLEFT : [0, 3]; \
HASTOLEFT : [0, 2]; \
HASBEHIND : [1, 0]; \
HASTOLEFT : [3, 0]; \
HASBEHIND : [0, 1]; \
"
model scenic.simulators.carla.model

o3 = Car with color[0.85546875, 0.74609375, 0.41015625]
o2 = Car left of o3 by Range(10, 20), with color[0.29296875, 0.46484375, 0.61328125]
ego = Car left of o2 by Range(0, 10), with color[0.734375, 0.72265625, 0.71484375]
o1 = Car left of o3 by Range(20, 50), with color[0.7578125, 0.359375, 0.33203125]

require o2 can see o1
require (distance from o1 to ego) <= 10 
require (distance from o2 to o1) <= 10 
require 10 <= (distance from o3 to ego) <= 20 

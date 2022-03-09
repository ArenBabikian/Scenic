param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASBEHIND : [0, 1]; \
HASBEHIND : [3, 2]; \
HASTOLEFT : [3, 0]; \
HASTOLEFT : [2, 1]; \
HASTOLEFT : [2, 0]; \
HASINFRONT : [2, 3]; \
HASTORIGHT : [0, 3]; \
"
model scenic.simulators.carla.model

o1 = Car with color[0.7578125, 0.359375, 0.33203125]
o2 = Car left of o1 by Range(0, 10), with color[0.29296875, 0.46484375, 0.61328125]
ego = Car behind o1 by Range(10, 20), with color[0.734375, 0.72265625, 0.71484375]
o3 = Car left of o1 by Range(20, 50), with color[0.85546875, 0.74609375, 0.41015625]

require o2 can see ego
require o2 can see o3
require 10 <= (distance from o2 to ego) <= 20 
require 10 <= (distance from o3 to ego) <= 20 
require 10 <= (distance from o3 to o2) <= 20 

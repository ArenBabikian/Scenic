param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASTOLEFT : [2, 0]; \
HASTOLEFT : [3, 1]; \
HASTOLEFT : [3, 4]; \
HASINFRONT : [0, 1]; \
HASINFRONT : [3, 2]; \
HASINFRONT : [0, 4]; \
HASBEHIND : [1, 0]; \
HASTOLEFT : [0, 2]; \
HASINFRONT : [0, 3]; \
HASINFRONT : [4, 3]; \
HASBEHIND : [2, 3]; \
"
model scenic.simulators.carla.model

o1 = Car with color[0.7578125, 0.359375, 0.33203125]
o4 = Car right of o1 by Range(0, 10), with color[0.265625, 0.625, 0.52734375]
ego = Car left of o4 by Range(20, 50), with color[0.734375, 0.72265625, 0.71484375]
o2 = Car left of o4 by Range(20, 50), with color[0.29296875, 0.46484375, 0.61328125]
o3 = Car left of o1 by Range(10, 20), with color[0.85546875, 0.74609375, 0.41015625]

require ego can see o1
require ego can see o3
require ego can see o4
require o1 can see o4
require o3 can see ego
require o3 can see o2
require o4 can see o1
require o4 can see o3
require 10 <= (distance from o2 to ego) <= 20 
require 20 <= (distance from o1 to ego) <= 50 
require 20 <= (distance from o2 to o1) <= 50 
require 20 <= (distance from o3 to ego) <= 50 
require 20 <= (distance from o3 to o2) <= 50 
require 20 <= (distance from o4 to o3) <= 50 

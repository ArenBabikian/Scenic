param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASBEHIND : [4, 3]; \
HASTOLEFT : [4, 1]; \
HASTOLEFT : [0, 1]; \
HASTOLEFT : [4, 2]; \
HASTOLEFT : [0, 3]; \
HASTOLEFT : [2, 3]; \
HASBEHIND : [1, 3]; \
HASTOLEFT : [4, 0]; \
HASTOLEFT : [2, 1]; \
HASTOLEFT : [1, 0]; \
HASTOLEFT : [1, 2]; \
HASTOLEFT : [0, 4]; \
HASINFRONT : [3, 4]; \
HASTOLEFT : [2, 4]; \
"
model scenic.simulators.carla.model

o3 = Car with color[0.85546875, 0.74609375, 0.41015625]
o1 = Car ahead of o3 by Range(20, 50), with color[0.7578125, 0.359375, 0.33203125]
ego = Car left of o3 by Range(20, 50), with color[0.734375, 0.72265625, 0.71484375]
o2 = Car left of o3 by Range(20, 50), with color[0.29296875, 0.46484375, 0.61328125]
o4 = Car right of o1 by Range(0, 10), with color[0.265625, 0.625, 0.52734375]

require o2 can see ego
require o3 can see o1
require o3 can see o4
require 20 <= (distance from o1 to ego) <= 50 
require 20 <= (distance from o2 to ego) <= 50 
require 20 <= (distance from o2 to o1) <= 50 
require 20 <= (distance from o4 to ego) <= 50 
require 20 <= (distance from o4 to o2) <= 50 
require 20 <= (distance from o4 to o3) <= 50 

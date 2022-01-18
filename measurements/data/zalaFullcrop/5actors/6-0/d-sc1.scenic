param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASTORIGHT : [4, 1]; \
HASTOLEFT : [4, 0]; \
HASINFRONT : [4, 2]; \
HASTOLEFT : [3, 2]; \
HASTORIGHT : [0, 1]; \
HASINFRONT : [0, 3]; \
HASBEHIND : [2, 1]; \
HASTOLEFT : [1, 0]; \
HASBEHIND : [2, 4]; \
HASTOLEFT : [1, 4]; \
"
model scenic.simulators.carla.model

o1 = Car with color[0.7578125, 0.359375, 0.33203125]
o2 = Car ahead of o1 by Range(20, 50), with color[0.29296875, 0.46484375, 0.61328125]
o3 = Car left of o2 by Range(10, 20), with color[0.85546875, 0.74609375, 0.41015625]
ego = Car ahead of o3 by Range(20, 50), with color[0.734375, 0.72265625, 0.71484375]
o4 = Car right of ego by Range(0, 10), with color[0.265625, 0.625, 0.52734375]

require ego can see o2
require ego can see o3
require o1 can see o2
require o1 can see o3
require o1 can see o4
require o3 can see ego
require o3 can see o1
require o3 can see o4
require o4 can see o2
require o4 can see o3
require (distance from o4 to o1) <= 10 
require 10 <= (distance from o1 to ego) <= 20 
require 20 <= (distance from o2 to ego) <= 50 
require 20 <= (distance from o3 to o1) <= 50 
require 20 <= (distance from o4 to o2) <= 50 
require 20 <= (distance from o4 to o3) <= 50 

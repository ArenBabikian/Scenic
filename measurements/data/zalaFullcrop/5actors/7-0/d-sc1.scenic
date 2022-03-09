param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASBEHIND : [4, 2]; \
HASTOLEFT : [4, 1]; \
HASBEHIND : [2, 0]; \
HASINFRONT : [3, 1]; \
HASINFRONT : [3, 0]; \
HASBEHIND : [2, 1]; \
HASINFRONT : [1, 0]; \
HASINFRONT : [3, 2]; \
HASINFRONT : [1, 2]; \
HASBEHIND : [0, 3]; \
HASINFRONT : [1, 3]; \
HASTOLEFT : [2, 4]; \
HASTORIGHT : [3, 4]; \
HASTORIGHT : [0, 4]; \
"
model scenic.simulators.carla.model

ego = Car with color[0.734375, 0.72265625, 0.71484375]
o1 = Car ahead of ego by Range(10, 20), with color[0.7578125, 0.359375, 0.33203125]
o2 = Car behind ego by Range(10, 20), with color[0.29296875, 0.46484375, 0.61328125]
o3 = Car ahead of o2 by Range(10, 20), with color[0.85546875, 0.74609375, 0.41015625]
o4 = Car left of o1 by Range(20, 50), with color[0.265625, 0.625, 0.52734375]

require ego can see o1
require o1 can see ego
require o1 can see o2
require o1 can see o3
require o2 can see o3
require o3 can see ego
require o3 can see o1
require o3 can see o2
require 20 <= (distance from o2 to o1) <= 50 
require 20 <= (distance from o3 to ego) <= 50 
require 20 <= (distance from o3 to o1) <= 50 
require 20 <= (distance from o4 to ego) <= 50 
require 20 <= (distance from o4 to o2) <= 50 
require 20 <= (distance from o4 to o3) <= 50 

param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASBEHIND : [3, 1]; \
HASTOLEFT : [2, 1]; \
HASTOLEFT : [2, 4]; \
HASBEHIND : [0, 1]; \
HASBEHIND : [3, 4]; \
HASBEHIND : [2, 0]; \
HASBEHIND : [3, 0]; \
HASBEHIND : [3, 2]; \
HASBEHIND : [1, 4]; \
HASTOLEFT : [0, 2]; \
HASBEHIND : [1, 2]; \
HASTOLEFT : [2, 3]; \
HASBEHIND : [0, 3]; \
HASINFRONT : [4, 3]; \
"
model scenic.simulators.carla.model

o4 = Car with color[0.265625, 0.625, 0.52734375]
o1 = Car ahead of o4 by Range(20, 50), with color[0.7578125, 0.359375, 0.33203125]
ego = Car behind o1 by Range(20, 50), with color[0.734375, 0.72265625, 0.71484375]
o2 = Car right of o4 by Range(20, 50), with color[0.29296875, 0.46484375, 0.61328125]
o3 = Car ahead of o1 by Range(10, 20), with color[0.85546875, 0.74609375, 0.41015625]

require o1 can see o3
require o4 can see o1
require o4 can see o3
require 10 <= (distance from o4 to ego) <= 20 
require 20 <= (distance from o2 to ego) <= 50 
require 20 <= (distance from o2 to o1) <= 50 
require 20 <= (distance from o3 to ego) <= 50 
require 20 <= (distance from o3 to o2) <= 50 
require 20 <= (distance from o4 to o3) <= 50 

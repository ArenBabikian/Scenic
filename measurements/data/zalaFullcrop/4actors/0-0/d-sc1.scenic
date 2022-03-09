param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASINFRONT : [2, 0]; \
HASTOLEFT : [1, 0]; \
HASBEHIND : [1, 3]; \
HASTOLEFT : [2, 3]; \
HASTOLEFT : [0, 3]; \
HASTOLEFT : [2, 1]; \
HASINFRONT : [3, 1]; \
HASTOLEFT : [3, 2]; \
HASTOLEFT : [1, 2]; \
"
model scenic.simulators.carla.model

o3 = Car with color[0.85546875, 0.74609375, 0.41015625]
ego = Car left of o3 by Range(20, 50), with color[0.734375, 0.72265625, 0.71484375]
o1 = Car left of ego by Range(20, 50), with color[0.7578125, 0.359375, 0.33203125]
o2 = Car behind ego by Range(20, 50), with color[0.29296875, 0.46484375, 0.61328125]

require o2 can see ego
require o3 can see o1
require (distance from o3 to o1) <= 10 
require 10 <= (distance from o2 to o1) <= 20 
require 20 <= (distance from o3 to o2) <= 50 

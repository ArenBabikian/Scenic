param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASTOLEFT : [1, 0]; \
HASBEHIND : [1, 2]; \
HASINFRONT : [3, 2]; \
HASTOLEFT : [3, 0]; \
HASTOLEFT : [2, 0]; \
HASINFRONT : [3, 1]; \
HASTOLEFT : [0, 1]; \
HASBEHIND : [1, 3]; \
HASTOLEFT : [0, 3]; \
"
model scenic.simulators.carla.model

ego = Car with color[0.734375, 0.72265625, 0.71484375]
o2 = Car left of ego by Range(10, 20), with color[0.29296875, 0.46484375, 0.61328125]
o1 = Car ahead of o2 by Range(0, 10), with color[0.7578125, 0.359375, 0.33203125]
o3 = Car behind o2 by Range(10, 20), with color[0.85546875, 0.74609375, 0.41015625]

require o2 can see o1
require o3 can see o1
require o3 can see o2
require 10 <= (distance from o1 to ego) <= 20 
require 20 <= (distance from o3 to ego) <= 50 
require 20 <= (distance from o3 to o1) <= 50 

param map = localPath('/usr/src/app/maps/tram05.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASBEHIND : [0, 2]; \
HASINFRONT : [3, 2]; \
HASINFRONT : [3, 1]; \
HASTOLEFT : [3, 0]; \
HASBEHIND : [1, 0]; \
HASTOLEFT : [2, 3]; \
HASBEHIND : [1, 3]; \
"
model scenic.simulators.carla.model

o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
o1 = Car left of o2 by Range(10, 20), with color[0.7578125, 0.359375, 0.33203125]
ego = Car left of o2 by Range(20, 50), with color[0.734375, 0.72265625, 0.71484375]
o3 = Car left of ego by Range(0, 10), with color[0.85546875, 0.74609375, 0.41015625]

require o1 can see o2
require o2 can see ego
require o3 can see o1
require o3 can see o2
require 10 <= (distance from o1 to ego) <= 20 
require 10 <= (distance from o3 to o1) <= 20 
require 20 <= (distance from o3 to o2) <= 50 

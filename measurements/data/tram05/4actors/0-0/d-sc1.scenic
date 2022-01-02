param map = localPath('/usr/src/app/maps/tram05.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASINFRONT : [2, 1]; \
HASTOLEFT : [3, 0]; \
HASTOLEFT : [3, 2]; \
HASTOLEFT : [2, 0]; \
HASBEHIND : [1, 2]; \
HASTOLEFT : [0, 3]; \
HASTOLEFT : [1, 3]; \
"
model scenic.simulators.carla.model

o1 = Car with color[0.7578125, 0.359375, 0.33203125]
ego = Car left of o1 by Range(20, 50), with color[0.734375, 0.72265625, 0.71484375]
o2 = Car right of ego by Range(20, 50), with color[0.29296875, 0.46484375, 0.61328125]
o3 = Car left of o2 by Range(20, 50), with color[0.85546875, 0.74609375, 0.41015625]

require ego can see o1
require ego can see o2
require ego can see o3
require o2 can see o1
require o3 can see ego
require (distance from o2 to o1) <= 10 
require (distance from o3 to ego) <= 10 
require 20 <= (distance from o3 to o1) <= 50 

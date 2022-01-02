param map = localPath('/usr/src/app/maps/tram05.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASTOLEFT : [2, 3]; \
HASINFRONT : [1, 0]; \
HASINFRONT : [1, 2]; \
HASTORIGHT : [0, 3]; \
HASTORIGHT : [3, 1]; \
HASBEHIND : [0, 1]; \
"
model scenic.simulators.carla.model

o3 = Car with color[0.85546875, 0.74609375, 0.41015625]
ego = Car right of o3 by Range(20, 50), with color[0.734375, 0.72265625, 0.71484375]
o2 = Car right of o3 by Range(10, 20), with color[0.29296875, 0.46484375, 0.61328125]
o1 = Car ahead of o2 by Range(10, 20), with color[0.7578125, 0.359375, 0.33203125]

require ego can see o2
require ego can see o3
require o1 can see ego
require o1 can see o2
require o1 can see o3
require o2 can see ego
require o2 can see o1
require (distance from o1 to ego) <= 10 
require (distance from o2 to ego) <= 10 
require 20 <= (distance from o3 to o1) <= 50 

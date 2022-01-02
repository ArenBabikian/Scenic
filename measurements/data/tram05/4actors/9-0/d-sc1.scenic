param map = localPath('/usr/src/app/maps/tram05.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASTORIGHT : [1, 3]; \
HASINFRONT : [0, 2]; \
HASINFRONT : [1, 2]; \
HASTORIGHT : [0, 3]; \
HASBEHIND : [3, 2]; \
HASTOLEFT : [0, 1]; \
HASBEHIND : [2, 0]; \
HASTORIGHT : [1, 0]; \
HASTORIGHT : [3, 1]; \
"
model scenic.simulators.carla.model

o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
o3 = Car right of o2 by Range(10, 20), with color[0.85546875, 0.74609375, 0.41015625]
o1 = Car behind o2 by Range(10, 20), with color[0.7578125, 0.359375, 0.33203125]
ego = Car right of o3 by Range(0, 10), with color[0.734375, 0.72265625, 0.71484375]

require ego can see o2
require ego can see o3
require o1 can see o2
require (distance from o1 to ego) <= 10 
require 10 <= (distance from o2 to ego) <= 20 
require 10 <= (distance from o3 to o1) <= 20 

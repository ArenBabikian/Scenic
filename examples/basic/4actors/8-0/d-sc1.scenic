param map = localPath('/usr/src/app/maps/town02.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASBEHIND : [0, 2]; \
HASBEHIND : [1, 2]; \
HASBEHIND : [0, 1]; \
HASINFRONT : [3, 2]; \
HASINFRONT : [1, 0]; \
HASTORIGHT : [3, 0]; \
HASTORIGHT : [3, 1]; \
"
model scenic.simulators.carla.model

o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
o3 = Car right of o2 by Range(0, 10), with color[0.85546875, 0.74609375, 0.41015625]
o1 = Car ahead of o2 by Range(20, 50), with color[0.7578125, 0.359375, 0.33203125]
ego = Car ahead of o2 by Range(20, 50), with color[0.734375, 0.72265625, 0.71484375]

require o1 can see ego
require o2 can see ego
require o2 can see o1
require o3 can see o2
require (distance from o1 to ego) <= 10 
require 20 <= (distance from o3 to ego) <= 50 
require 20 <= (distance from o3 to o1) <= 50 

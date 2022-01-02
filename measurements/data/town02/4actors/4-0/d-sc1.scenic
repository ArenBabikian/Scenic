param map = localPath('/usr/src/app/maps/town02.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASINFRONT : [2, 1]; \
HASBEHIND : [0, 3]; \
HASTORIGHT : [2, 0]; \
HASTOLEFT : [1, 0]; \
HASTORIGHT : [0, 2]; \
HASTORIGHT : [3, 2]; \
"
model scenic.simulators.carla.model

o1 = Car with color[0.7578125, 0.359375, 0.33203125]
o3 = Car left of o1 by Range(10, 20), with color[0.85546875, 0.74609375, 0.41015625]
ego = Car ahead of o3 by Range(0, 10), with color[0.734375, 0.72265625, 0.71484375]
o2 = Car ahead of o1 by Range(10, 20), with color[0.29296875, 0.46484375, 0.61328125]

require o1 can see o2
require o2 can see ego
require o2 can see o1
require o2 can see o3
require o3 can see ego
require 20 <= (distance from o1 to ego) <= 50 
require 20 <= (distance from o2 to ego) <= 50 
require 20 <= (distance from o3 to o2) <= 50 

param map = localPath('/usr/src/app/maps/town02.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASTOLEFT : [1, 3]; \
HASTOLEFT : [2, 0]; \
HASBEHIND : [2, 1]; \
HASINFRONT : [0, 3]; \
HASINFRONT : [0, 1]; \
HASTOLEFT : [1, 2]; \
HASINFRONT : [0, 2]; \
"
model scenic.simulators.carla.model

o3 = Car with color[0.85546875, 0.74609375, 0.41015625]
ego = Car ahead of o3 by Range(0, 10), with color[0.734375, 0.72265625, 0.71484375]
o1 = Car behind o3 by Range(10, 20), with color[0.7578125, 0.359375, 0.33203125]
o2 = Car behind o3 by Range(10, 20), with color[0.29296875, 0.46484375, 0.61328125]

require ego can see o1
require ego can see o2
require ego can see o3
require o2 can see ego
require o2 can see o3
require o3 can see ego
require (distance from o2 to o1) <= 10 
require 20 <= (distance from o1 to ego) <= 50 
require 20 <= (distance from o2 to ego) <= 50 

param map = localPath('/usr/src/app/maps/town02.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASBEHIND : [1, 2]; \
HASTOLEFT : [0, 3]; \
HASBEHIND : [1, 0]; \
HASBEHIND : [3, 2]; \
HASINFRONT : [2, 0]; \
HASTOLEFT : [3, 1]; \
HASTOLEFT : [0, 1]; \
"
model scenic.simulators.carla.model

o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
o3 = Car left of o2 by Range(10, 20), with color[0.85546875, 0.74609375, 0.41015625]
ego = Car behind o3 by Range(10, 20), with color[0.734375, 0.72265625, 0.71484375]
o1 = Car behind o2 by Range(10, 20), with color[0.7578125, 0.359375, 0.33203125]

require ego can see o3
require o2 can see ego
require (distance from o2 to ego) <= 10 
require 20 <= (distance from o1 to ego) <= 50 
require 20 <= (distance from o3 to o1) <= 50 

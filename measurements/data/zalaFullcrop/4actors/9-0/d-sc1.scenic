param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASTORIGHT : [0, 1]; \
HASINFRONT : [3, 1]; \
HASBEHIND : [0, 2]; \
HASTOLEFT : [1, 0]; \
"
model scenic.simulators.carla.model

o1 = Car with color[0.7578125, 0.359375, 0.33203125]
o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
ego = Car behind o2 by Range(20, 50), with color[0.734375, 0.72265625, 0.71484375]
o3 = Car behind o1 by Range(10, 20), with color[0.85546875, 0.74609375, 0.41015625]

require o3 can see ego
require o3 can see o1
require (distance from o1 to ego) <= 10 
require (distance from o3 to ego) <= 10 
require 10 <= (distance from o3 to o2) <= 20 
require 20 <= (distance from o2 to o1) <= 50 

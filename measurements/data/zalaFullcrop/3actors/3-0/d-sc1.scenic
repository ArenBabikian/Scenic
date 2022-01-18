param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASBEHIND : [2, 1]; \
HASINFRONT : [2, 0]; \
HASBEHIND : [0, 1]; \
HASINFRONT : [1, 2]; \
"
model scenic.simulators.carla.model

o1 = Car with color[0.7578125, 0.359375, 0.33203125]
ego = Car ahead of o1 by Range(20, 50), with color[0.734375, 0.72265625, 0.71484375]
o2 = Car behind ego by Range(10, 20), with color[0.29296875, 0.46484375, 0.61328125]

require o1 can see ego
require o1 can see o2
require o2 can see ego
require (distance from o2 to o1) <= 10 

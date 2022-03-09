param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASINFRONT : [0, 2]; \
HASINFRONT : [1, 0]; \
"
model scenic.simulators.carla.model

o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
o1 = Car ahead of o2 by Range(10, 20), with color[0.7578125, 0.359375, 0.33203125]
ego = Car behind o2 by Range(0, 10), with color[0.734375, 0.72265625, 0.71484375]

require ego can see o1
require ego can see o2
require o1 can see ego
require o1 can see o2
require o2 can see o1
require 10 <= (distance from o1 to ego) <= 20 

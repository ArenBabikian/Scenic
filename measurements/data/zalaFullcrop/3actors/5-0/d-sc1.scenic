param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASBEHIND : [1, 0]; \
HASBEHIND : [2, 0]; \
HASINFRONT : [2, 1]; \
HASINFRONT : [0, 2]; \
"
model scenic.simulators.carla.model

ego = Car with color[0.734375, 0.72265625, 0.71484375]
o1 = Car ahead of ego by Range(20, 50), with color[0.7578125, 0.359375, 0.33203125]
o2 = Car behind o1 by Range(10, 20), with color[0.29296875, 0.46484375, 0.61328125]

require ego can see o1
require ego can see o2
require o2 can see o1
require 10 <= (distance from o2 to ego) <= 20 

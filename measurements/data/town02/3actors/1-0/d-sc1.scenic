param map = localPath('/usr/src/app/maps/town02.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASBEHIND : [2, 0]; \
HASBEHIND : [1, 0]; \
HASBEHIND : [1, 2]; \
HASINFRONT : [0, 1]; \
"
model scenic.simulators.carla.model

ego = Car with color[0.734375, 0.72265625, 0.71484375]
o2 = Car ahead of ego by Range(10, 20), with color[0.29296875, 0.46484375, 0.61328125]
o1 = Car ahead of o2 by Range(10, 20), with color[0.7578125, 0.359375, 0.33203125]

require ego can see o1
require ego can see o2
require o2 can see o1
require 20 <= (distance from o1 to ego) <= 50 

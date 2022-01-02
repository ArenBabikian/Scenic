param map = localPath('/usr/src/app/maps/tram05.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASBEHIND : [1, 2]; \
HASBEHIND : [1, 0]; \
HASBEHIND : [2, 1]; \
"
model scenic.simulators.carla.model

o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
ego = Car behind o2 by Range(20, 50), with color[0.734375, 0.72265625, 0.71484375]
o1 = Car right of ego by Range(0, 10), with color[0.7578125, 0.359375, 0.33203125]

require ego can see o2
require 20 <= (distance from o2 to o1) <= 50 

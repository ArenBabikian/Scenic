param map = localPath('/usr/src/app/maps/tram05.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASINFRONT : [2, 1]; \
HASTOLEFT : [0, 1]; \
HASINFRONT : [0, 2]; \
HASINFRONT : [2, 0]; \
"
model scenic.simulators.carla.model

o1 = Car with color[0.7578125, 0.359375, 0.33203125]
o2 = Car behind o1 by Range(10, 20), with color[0.29296875, 0.46484375, 0.61328125]
ego = Car left of o1 by Range(0, 10), with color[0.734375, 0.72265625, 0.71484375]

require ego can see o2
require o1 can see ego
require o2 can see ego
require o2 can see o1
require 20 <= (distance from o2 to ego) <= 50 

param map = localPath('/usr/src/app/maps/tram05.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASBEHIND : [1, 2]; \
"
model scenic.simulators.carla.model

ego = Car with color[0.734375, 0.72265625, 0.71484375]
o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
o1 = Car in SectorRegion(o2, 50, o2.heading+math.pi, math.atan(2/5)), with color[0.7578125, 0.359375, 0.33203125]

require o1 can see ego
require (distance from o1 to ego) <= 10 
require 10 <= (distance from o2 to o1) <= 20 
require 20 <= (distance from o2 to ego) <= 50 

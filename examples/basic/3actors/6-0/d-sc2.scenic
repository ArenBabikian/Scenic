param map = localPath('/usr/src/app/maps/town02.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASINFRONT : [0, 1]; \
HASTOLEFT : [0, 2]; \
HASBEHIND : [1, 2]; \
"
model scenic.simulators.carla.model

o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
o1 = Car in SectorRegion(o2, 50, o2.heading+math.pi, math.atan(2/5)), with color[0.7578125, 0.359375, 0.33203125]
ego = Car in SectorRegion(o2, 20, o2.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o1, 50, o1.heading+math.pi, math.atan(2/5))), with color[0.734375, 0.72265625, 0.71484375]

require ego can see o1
require (distance from o2 to ego) <= 10 
require 10 <= (distance from o1 to ego) <= 20 
require 10 <= (distance from o2 to o1) <= 20 

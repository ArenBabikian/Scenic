param map = localPath('/usr/src/app/maps/town02.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASINFRONT : [0, 1]; \
"
model scenic.simulators.carla.model

o1 = Car with color[0.7578125, 0.359375, 0.33203125]
ego = Car in SectorRegion(o1, 50, o1.heading+math.pi, math.atan(2/5)), with color[0.734375, 0.72265625, 0.71484375]

require ego can see o1
require 10 <= (distance from o1 to ego) <= 20 

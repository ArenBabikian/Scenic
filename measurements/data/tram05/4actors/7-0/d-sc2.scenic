param map = localPath('/usr/src/app/maps/tram05.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASINFRONT : [1, 3]; \
HASINFRONT : [1, 0]; \
HASTOLEFT : [1, 2]; \
HASINFRONT : [3, 0]; \
"
model scenic.simulators.carla.model

ego = Car with color[0.734375, 0.72265625, 0.71484375]
o2 = Car in SectorRegion(ego, 50, ego.heading+math.pi, math.atan(2/5)), with color[0.29296875, 0.46484375, 0.61328125]
o3 = Car in SectorRegion(ego, 50, ego.heading+math.pi, math.atan(2/5)), with color[0.85546875, 0.74609375, 0.41015625]
o1 = Car in SectorRegion(o2, 20, o2.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(ego, 50, ego.heading+math.pi, math.atan(2/5))).intersect(SectorRegion(o3, 50, o3.heading+math.pi, math.atan(2/5))), with color[0.7578125, 0.359375, 0.33203125]

require o1 can see ego
require o1 can see o3
require o3 can see ego
require (distance from o2 to o1) <= 10 
require (distance from o3 to ego) <= 10 
require (distance from o3 to o1) <= 10 
require 10 <= (distance from o1 to ego) <= 20 
require 10 <= (distance from o2 to ego) <= 20 
require 10 <= (distance from o3 to o2) <= 20 

param map = localPath('/usr/src/app/maps/tram05.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASTOLEFT : [0, 3]; \
HASBEHIND : [0, 2]; \
HASBEHIND : [1, 3]; \
HASTOLEFT : [2, 3]; \
"
model scenic.simulators.carla.model

o3 = Car with color[0.85546875, 0.74609375, 0.41015625]
o2 = Car in SectorRegion(o3, 50, o3.heading, math.atan(2/5)), with color[0.29296875, 0.46484375, 0.61328125]
o1 = Car in SectorRegion(o2, 20, o2.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o3, 50, o3.heading, math.atan(2/5))), with color[0.7578125, 0.359375, 0.33203125]
ego = Car in SectorRegion(o2, 20, o2.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o3, 20, o3.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o1, 50, o1.heading+math.pi, math.atan(2/5))), with color[0.734375, 0.72265625, 0.71484375]

require o1 can see o2
require o2 can see ego
require o3 can see o1
require o3 can see o2
require (distance from o3 to ego) <= 10 
require 10 <= (distance from o1 to ego) <= 20 
require 10 <= (distance from o2 to o1) <= 20 
require 10 <= (distance from o3 to o1) <= 20 
require 20 <= (distance from o2 to ego) <= 50 
require 20 <= (distance from o3 to o2) <= 50 

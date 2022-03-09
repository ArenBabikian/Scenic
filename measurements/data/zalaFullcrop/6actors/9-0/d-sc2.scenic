param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASTOLEFT : [1, 5]; \
HASTOLEFT : [3, 5]; \
HASBEHIND : [1, 2]; \
HASTORIGHT : [4, 2]; \
HASTOLEFT : [0, 2]; \
HASTOLEFT : [3, 1]; \
HASTOLEFT : [0, 1]; \
HASINFRONT : [3, 4]; \
HASTOLEFT : [1, 4]; \
HASINFRONT : [3, 0]; \
HASBEHIND : [2, 5]; \
"
model scenic.simulators.carla.model

o5 = Car with color[0.76953125, 0.6484375, 0.5234375]
o2 = Car in SectorRegion(o5, 50, o5.heading, math.atan(2/5)), with color[0.29296875, 0.46484375, 0.61328125]
o4 = Car in SectorRegion(o2, 20, o2.heading-(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o5, 50, o5.heading, math.atan(2/5))), with color[0.265625, 0.625, 0.52734375]
o1 = Car in SectorRegion(o5, 20, o5.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o4, 20, o4.heading-(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o2, 50, o2.heading+math.pi, math.atan(2/5))), with color[0.7578125, 0.359375, 0.33203125]
ego = Car in SectorRegion(o1, 20, o1.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o2, 20, o2.heading-(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o5, 50, o5.heading, math.atan(2/5))), with color[0.734375, 0.72265625, 0.71484375]
o3 = Car in SectorRegion(o1, 20, o1.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o5, 20, o5.heading-(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(ego, 50, ego.heading+math.pi, math.atan(2/5))).intersect(SectorRegion(o4, 50, o4.heading, math.atan(2/5))), with color[0.85546875, 0.74609375, 0.41015625]

require ego can see o4
require o1 can see o5
require o3 can see ego
require o3 can see o2
require o3 can see o4
require o4 can see ego
require o4 can see o3
require o4 can see o5
require o5 can see ego
require o5 can see o1
require o5 can see o2
require o5 can see o4
require (distance from o4 to ego) <= 10 
require 10 <= (distance from o2 to ego) <= 20 
require 10 <= (distance from o4 to o2) <= 20 
require 10 <= (distance from o5 to o1) <= 20 
require 20 <= (distance from o1 to ego) <= 50 
require 20 <= (distance from o2 to o1) <= 50 
require 20 <= (distance from o3 to ego) <= 50 
require 20 <= (distance from o3 to o1) <= 50 
require 20 <= (distance from o3 to o2) <= 50 
require 20 <= (distance from o4 to o1) <= 50 
require 20 <= (distance from o4 to o3) <= 50 
require 20 <= (distance from o5 to ego) <= 50 
require 20 <= (distance from o5 to o2) <= 50 
require 20 <= (distance from o5 to o3) <= 50 
require 20 <= (distance from o5 to o4) <= 50 

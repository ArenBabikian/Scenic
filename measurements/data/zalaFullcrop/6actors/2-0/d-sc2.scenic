param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASTORIGHT : [1, 5]; \
HASBEHIND : [4, 5]; \
HASTORIGHT : [1, 0]; \
HASBEHIND : [4, 3]; \
HASINFRONT : [4, 0]; \
HASTOLEFT : [2, 5]; \
HASTOLEFT : [2, 4]; \
HASINFRONT : [3, 0]; \
HASTORIGHT : [1, 4]; \
HASINFRONT : [5, 0]; \
HASTORIGHT : [1, 2]; \
HASBEHIND : [5, 3]; \
"
model scenic.simulators.carla.model

ego = Car with color[0.734375, 0.72265625, 0.71484375]
o3 = Car in SectorRegion(ego, 20, ego.heading-(math.pi/2), math.atan(2.5/2)), with color[0.85546875, 0.74609375, 0.41015625]
o5 = Car in SectorRegion(ego, 20, ego.heading-(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o3, 50, o3.heading, math.atan(2/5))), with color[0.76953125, 0.6484375, 0.5234375]
o4 = Car in SectorRegion(ego, 20, ego.heading-(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o3, 50, o3.heading, math.atan(2/5))).intersect(SectorRegion(o5, 50, o5.heading, math.atan(2/5))), with color[0.265625, 0.625, 0.52734375]
o2 = Car in SectorRegion(o4, 20, o4.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o5, 20, o5.heading+(math.pi/2), math.atan(2.5/2))), with color[0.29296875, 0.46484375, 0.61328125]
o1 = Car in SectorRegion(o2, 20, o2.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(ego, 20, ego.heading-(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o3, 20, o3.heading-(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o4, 20, o4.heading-(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o5, 20, o5.heading-(math.pi/2), math.atan(2.5/2))), with color[0.7578125, 0.359375, 0.33203125]

require o1 can see o3
require o2 can see o3
require o3 can see ego
require o3 can see o2
require o3 can see o4
require o3 can see o5
require o4 can see ego
require o5 can see ego
require o5 can see o4
require 10 <= (distance from o4 to ego) <= 20 
require 10 <= (distance from o5 to o2) <= 20 
require 10 <= (distance from o5 to o3) <= 20 
require 10 <= (distance from o5 to o4) <= 20 
require 20 <= (distance from o1 to ego) <= 50 
require 20 <= (distance from o2 to ego) <= 50 
require 20 <= (distance from o2 to o1) <= 50 
require 20 <= (distance from o3 to ego) <= 50 
require 20 <= (distance from o3 to o1) <= 50 
require 20 <= (distance from o3 to o2) <= 50 
require 20 <= (distance from o4 to o1) <= 50 
require 20 <= (distance from o4 to o2) <= 50 
require 20 <= (distance from o4 to o3) <= 50 
require 20 <= (distance from o5 to ego) <= 50 
require 20 <= (distance from o5 to o1) <= 50 

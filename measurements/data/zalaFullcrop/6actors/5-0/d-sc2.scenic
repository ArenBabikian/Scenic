param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASTORIGHT : [5, 3]; \
HASINFRONT : [0, 3]; \
HASBEHIND : [1, 3]; \
HASTOLEFT : [2, 3]; \
HASBEHIND : [2, 4]; \
HASINFRONT : [5, 1]; \
HASINFRONT : [0, 1]; \
HASTOLEFT : [2, 0]; \
HASTOLEFT : [1, 4]; \
HASTOLEFT : [2, 5]; \
HASTOLEFT : [4, 3]; \
HASINFRONT : [0, 5]; \
"
model scenic.simulators.carla.model

o3 = Car with color[0.85546875, 0.74609375, 0.41015625]
o4 = Car in SectorRegion(o3, 20, o3.heading+(math.pi/2), math.atan(2.5/2)), with color[0.265625, 0.625, 0.52734375]
o1 = Car in SectorRegion(o4, 20, o4.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o3, 50, o3.heading, math.atan(2/5))), with color[0.7578125, 0.359375, 0.33203125]
o5 = Car in SectorRegion(o3, 20, o3.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o1, 50, o1.heading+math.pi, math.atan(2/5))), with color[0.76953125, 0.6484375, 0.5234375]
ego = Car in SectorRegion(o1, 50, o1.heading+math.pi, math.atan(2/5)).intersect(SectorRegion(o3, 50, o3.heading+math.pi, math.atan(2/5))).intersect(SectorRegion(o5, 50, o5.heading+math.pi, math.atan(2/5))), with color[0.734375, 0.72265625, 0.71484375]
o2 = Car in SectorRegion(ego, 20, ego.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o3, 20, o3.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o5, 20, o5.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o4, 50, o4.heading, math.atan(2/5))), with color[0.29296875, 0.46484375, 0.61328125]

require ego can see o1
require ego can see o3
require ego can see o4
require ego can see o5
require o3 can see o1
require o3 can see o4
require o4 can see ego
require o4 can see o2
require o4 can see o3
require o4 can see o5
require o5 can see o1
require o5 can see o3
require o5 can see o4
require (distance from o5 to o3) <= 10 
require 10 <= (distance from o2 to ego) <= 20 
require 10 <= (distance from o3 to ego) <= 20 
require 10 <= (distance from o3 to o2) <= 20 
require 10 <= (distance from o4 to o1) <= 20 
require 10 <= (distance from o5 to ego) <= 20 
require 10 <= (distance from o5 to o2) <= 20 
require 20 <= (distance from o1 to ego) <= 50 
require 20 <= (distance from o2 to o1) <= 50 
require 20 <= (distance from o3 to o1) <= 50 
require 20 <= (distance from o4 to ego) <= 50 
require 20 <= (distance from o4 to o2) <= 50 
require 20 <= (distance from o4 to o3) <= 50 
require 20 <= (distance from o5 to o1) <= 50 
require 20 <= (distance from o5 to o4) <= 50 

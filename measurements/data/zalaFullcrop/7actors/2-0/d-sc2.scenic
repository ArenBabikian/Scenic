param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASTORIGHT : [1, 5]; \
HASINFRONT : [1, 3]; \
HASTOLEFT : [6, 5]; \
HASINFRONT : [0, 3]; \
HASTORIGHT : [0, 2]; \
HASINFRONT : [4, 5]; \
HASTORIGHT : [3, 5]; \
HASTOLEFT : [6, 1]; \
HASTORIGHT : [0, 1]; \
HASBEHIND : [3, 4]; \
HASINFRONT : [2, 5]; \
"
model scenic.simulators.carla.model

o5 = Car with color[0.76953125, 0.6484375, 0.5234375]
o2 = Car in SectorRegion(o5, 20, o5.heading+(math.pi/2), math.atan(2.5/2)), with color[0.29296875, 0.46484375, 0.61328125]
o4 = Car in SectorRegion(o5, 20, o5.heading+(math.pi/2), math.atan(2.5/2)), with color[0.265625, 0.625, 0.52734375]
o3 = Car in SectorRegion(o5, 20, o5.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o4, 50, o4.heading, math.atan(2/5))), with color[0.85546875, 0.74609375, 0.41015625]
o1 = Car in SectorRegion(o5, 20, o5.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o3, 20, o3.heading-(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o2, 50, o2.heading, math.atan(2/5))).intersect(SectorRegion(o4, 50, o4.heading, math.atan(2/5))), with color[0.7578125, 0.359375, 0.33203125]
ego = Car in SectorRegion(o1, 20, o1.heading+(math.pi/2), math.atan(2.5/2)).intersect(SectorRegion(o2, 20, o2.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o5, 20, o5.heading+(math.pi/2), math.atan(2.5/2))).intersect(SectorRegion(o3, 50, o3.heading+math.pi, math.atan(2/5))), with color[0.734375, 0.72265625, 0.71484375]
o6 = Car in SectorRegion(ego, 50, ego.heading, math.atan(2/5)).intersect(SectorRegion(o1, 50, o1.heading, math.atan(2/5))).intersect(SectorRegion(o5, 50, o5.heading, math.atan(2/5))), with color[0.1953125, 0.1953125, 0.1953125]

require ego can see o3
require ego can see o5
require ego can see o6
require o1 can see o3
require o1 can see o6
require o2 can see o1
require o2 can see o3
require o2 can see o5
require o2 can see o6
require o3 can see o5
require o3 can see o6
require o4 can see ego
require o4 can see o1
require o4 can see o2
require o4 can see o3
require o4 can see o5
require o4 can see o6
require o5 can see o3
require o5 can see o6
require o6 can see ego
require o6 can see o1
require o6 can see o2
require o6 can see o3
require o6 can see o4
require (distance from o4 to o2) <= 10 
require 10 <= (distance from o1 to ego) <= 20 
require 10 <= (distance from o2 to ego) <= 20 
require 10 <= (distance from o2 to o1) <= 20 
require 10 <= (distance from o3 to ego) <= 20 
require 10 <= (distance from o3 to o1) <= 20 
require 10 <= (distance from o4 to ego) <= 20 
require 10 <= (distance from o4 to o1) <= 20 
require 20 <= (distance from o3 to o2) <= 50 
require 20 <= (distance from o4 to o3) <= 50 
require 20 <= (distance from o5 to ego) <= 50 
require 20 <= (distance from o5 to o1) <= 50 
require 20 <= (distance from o5 to o2) <= 50 
require 20 <= (distance from o5 to o3) <= 50 
require 20 <= (distance from o5 to o4) <= 50 
require 20 <= (distance from o6 to ego) <= 50 
require 20 <= (distance from o6 to o1) <= 50 
require 20 <= (distance from o6 to o2) <= 50 
require 20 <= (distance from o6 to o3) <= 50 
require 20 <= (distance from o6 to o4) <= 50 
require 20 <= (distance from o6 to o5) <= 50 

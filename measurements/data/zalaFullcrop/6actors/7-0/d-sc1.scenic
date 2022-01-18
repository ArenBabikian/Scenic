param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASBEHIND : [1, 0]; \
HASBEHIND : [1, 2]; \
HASTOLEFT : [5, 3]; \
HASBEHIND : [3, 2]; \
HASBEHIND : [3, 0]; \
HASTOLEFT : [4, 1]; \
HASTOLEFT : [5, 1]; \
HASINFRONT : [0, 2]; \
HASINFRONT : [0, 1]; \
HASINFRONT : [2, 3]; \
HASINFRONT : [0, 4]; \
HASTOLEFT : [3, 5]; \
"
model scenic.simulators.carla.model

o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
ego = Car behind o2 by Range(0, 10), with color[0.734375, 0.72265625, 0.71484375]
o1 = Car ahead of o2 by Range(20, 50), with color[0.7578125, 0.359375, 0.33203125]
o3 = Car ahead of ego by Range(10, 20), with color[0.85546875, 0.74609375, 0.41015625]
o4 = Car left of o1 by Range(10, 20), with color[0.265625, 0.625, 0.52734375]
o5 = Car left of o1 by Range(10, 20), with color[0.76953125, 0.6484375, 0.5234375]

require ego can see o1
require ego can see o2
require ego can see o3
require ego can see o4
require ego can see o5
require o1 can see o4
require o2 can see o1
require o2 can see o3
require o2 can see o4
require o2 can see o5
require o3 can see o1
require o3 can see o4
require o4 can see ego
require o4 can see o1
require o4 can see o2
require o4 can see o3
require o4 can see o5
require o5 can see ego
require o5 can see o2
require 10 <= (distance from o3 to o2) <= 20 
require 10 <= (distance from o5 to o4) <= 20 
require 20 <= (distance from o1 to ego) <= 50 
require 20 <= (distance from o3 to o1) <= 50 
require 20 <= (distance from o4 to ego) <= 50 
require 20 <= (distance from o4 to o2) <= 50 
require 20 <= (distance from o4 to o3) <= 50 
require 20 <= (distance from o5 to ego) <= 50 
require 20 <= (distance from o5 to o2) <= 50 
require 20 <= (distance from o5 to o3) <= 50 

param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASBEHIND : [2, 3]; \
HASBEHIND : [1, 3]; \
HASTORIGHT : [4, 3]; \
HASBEHIND : [2, 0]; \
HASTOLEFT : [1, 5]; \
HASTOLEFT : [4, 5]; \
HASBEHIND : [2, 1]; \
HASINFRONT : [4, 1]; \
HASBEHIND : [0, 3]; \
HASTOLEFT : [5, 0]; \
HASBEHIND : [2, 4]; \
HASTOLEFT : [3, 1]; \
HASTOLEFT : [3, 2]; \
HASINFRONT : [1, 2]; \
HASINFRONT : [0, 2]; \
HASTOLEFT : [5, 2]; \
HASBEHIND : [1, 4]; \
HASINFRONT : [5, 4]; \
HASTOLEFT : [3, 5]; \
"
model scenic.simulators.carla.model

o3 = Car with color[0.85546875, 0.74609375, 0.41015625]
ego = Car left of o3 by Range(0, 10), with color[0.734375, 0.72265625, 0.71484375]
o5 = Car left of ego by Range(20, 50), with color[0.76953125, 0.6484375, 0.5234375]
o1 = Car left of o5 by Range(20, 50), with color[0.7578125, 0.359375, 0.33203125]
o4 = Car behind o3 by Range(10, 20), with color[0.265625, 0.625, 0.52734375]
o2 = Car ahead of o4 by Range(20, 50), with color[0.29296875, 0.46484375, 0.61328125]

require ego can see o1
require ego can see o2
require o1 can see o2
require o4 can see ego
require o4 can see o1
require o4 can see o2
require o4 can see o3
require o5 can see ego
require o5 can see o3
require o5 can see o4
require (distance from o2 to o1) <= 10 
require 10 <= (distance from o1 to ego) <= 20 
require 20 <= (distance from o2 to ego) <= 50 
require 20 <= (distance from o3 to o1) <= 50 
require 20 <= (distance from o3 to o2) <= 50 
require 20 <= (distance from o4 to ego) <= 50 
require 20 <= (distance from o4 to o1) <= 50 
require 20 <= (distance from o5 to o2) <= 50 
require 20 <= (distance from o5 to o3) <= 50 
require 20 <= (distance from o5 to o4) <= 50 

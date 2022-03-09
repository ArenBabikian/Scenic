param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASTOLEFT : [1, 3]; \
HASINFRONT : [1, 5]; \
HASINFRONT : [1, 2]; \
HASTOLEFT : [0, 3]; \
HASTOLEFT : [4, 3]; \
HASBEHIND : [4, 5]; \
HASTOLEFT : [5, 2]; \
HASINFRONT : [5, 3]; \
HASTORIGHT : [1, 0]; \
HASTOLEFT : [4, 0]; \
HASBEHIND : [3, 2]; \
HASINFRONT : [2, 1]; \
HASTOLEFT : [3, 1]; \
HASTOLEFT : [4, 1]; \
HASINFRONT : [5, 1]; \
HASTOLEFT : [0, 4]; \
HASTORIGHT : [2, 4]; \
HASTORIGHT : [5, 4]; \
HASBEHIND : [3, 5]; \
"
model scenic.simulators.carla.model

o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
o3 = Car ahead of o2 by Range(20, 50), with color[0.85546875, 0.74609375, 0.41015625]
ego = Car left of o3 by Range(10, 20), with color[0.734375, 0.72265625, 0.71484375]
o5 = Car right of o2 by Range(0, 10), with color[0.76953125, 0.6484375, 0.5234375]
o4 = Car behind o3 by Range(20, 50), with color[0.265625, 0.625, 0.52734375]
o1 = Car left of ego by Range(0, 10), with color[0.7578125, 0.359375, 0.33203125]

require ego can see o2
require ego can see o4
require ego can see o5
require o1 can see ego
require o1 can see o2
require o1 can see o4
require o1 can see o5
require o2 can see ego
require o2 can see o1
require o2 can see o3
require o5 can see ego
require o5 can see o1
require o5 can see o2
require o5 can see o3
require (distance from o3 to o1) <= 10 
require 10 <= (distance from o4 to o2) <= 20 
require 10 <= (distance from o5 to o4) <= 20 
require 20 <= (distance from o2 to ego) <= 50 
require 20 <= (distance from o2 to o1) <= 50 
require 20 <= (distance from o4 to ego) <= 50 
require 20 <= (distance from o4 to o1) <= 50 
require 20 <= (distance from o5 to ego) <= 50 
require 20 <= (distance from o5 to o1) <= 50 
require 20 <= (distance from o5 to o3) <= 50 

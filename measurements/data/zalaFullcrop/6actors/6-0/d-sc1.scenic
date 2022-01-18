param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASBEHIND : [3, 5]; \
HASINFRONT : [0, 5]; \
HASBEHIND : [3, 2]; \
HASBEHIND : [4, 5]; \
HASBEHIND : [4, 1]; \
HASBEHIND : [2, 5]; \
HASBEHIND : [3, 0]; \
HASTOLEFT : [1, 2]; \
HASTORIGHT : [0, 4]; \
HASTORIGHT : [4, 0]; \
HASBEHIND : [5, 0]; \
HASTOLEFT : [2, 1]; \
HASTOLEFT : [1, 3]; \
HASBEHIND : [5, 3]; \
HASTORIGHT : [4, 3]; \
HASBEHIND : [0, 3]; \
HASTOLEFT : [2, 4]; \
HASTORIGHT : [5, 4]; \
"
model scenic.simulators.carla.model

o5 = Car with color[0.76953125, 0.6484375, 0.5234375]
o2 = Car behind o5 by Range(20, 50), with color[0.29296875, 0.46484375, 0.61328125]
o1 = Car right of o5 by Range(20, 50), with color[0.7578125, 0.359375, 0.33203125]
o4 = Car behind o1 by Range(0, 10), with color[0.265625, 0.625, 0.52734375]
ego = Car left of o1 by Range(20, 50), with color[0.734375, 0.72265625, 0.71484375]
o3 = Car ahead of o2 by Range(10, 20), with color[0.85546875, 0.74609375, 0.41015625]

require ego can see o1
require ego can see o2
require ego can see o4
require ego can see o5
require o1 can see o2
require o1 can see o5
require o2 can see ego
require o2 can see o3
require (distance from o2 to ego) <= 10 
require 10 <= (distance from o3 to ego) <= 20 
require 20 <= (distance from o2 to o1) <= 50 
require 20 <= (distance from o3 to o1) <= 50 
require 20 <= (distance from o4 to ego) <= 50 
require 20 <= (distance from o4 to o2) <= 50 
require 20 <= (distance from o4 to o3) <= 50 
require 20 <= (distance from o5 to ego) <= 50 
require 20 <= (distance from o5 to o3) <= 50 
require 20 <= (distance from o5 to o4) <= 50 

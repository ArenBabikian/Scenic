param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASTOLEFT : [4, 1]; \
HASTOLEFT : [0, 1]; \
HASBEHIND : [0, 5]; \
HASBEHIND : [4, 5]; \
HASTOLEFT : [4, 2]; \
HASBEHIND : [0, 3]; \
HASBEHIND : [5, 1]; \
HASTORIGHT : [2, 1]; \
HASTOLEFT : [5, 3]; \
HASTOLEFT : [2, 5]; \
HASINFRONT : [4, 0]; \
HASTORIGHT : [2, 0]; \
HASTOLEFT : [3, 0]; \
HASTOLEFT : [1, 0]; \
HASBEHIND : [5, 2]; \
HASINFRONT : [1, 2]; \
HASTOLEFT : [3, 4]; \
HASBEHIND : [5, 4]; \
HASBEHIND : [0, 4]; \
HASBEHIND : [2, 4]; \
HASINFRONT : [1, 5]; \
"
model scenic.simulators.carla.model

o1 = Car with color[0.7578125, 0.359375, 0.33203125]
o3 = Car left of o1 by Range(20, 50), with color[0.85546875, 0.74609375, 0.41015625]
o5 = Car right of o3 by Range(20, 50), with color[0.76953125, 0.6484375, 0.5234375]
o2 = Car behind o3 by Range(20, 50), with color[0.29296875, 0.46484375, 0.61328125]
ego = Car behind o5 by Range(20, 50), with color[0.734375, 0.72265625, 0.71484375]
o4 = Car left of o1 by Range(10, 20), with color[0.265625, 0.625, 0.52734375]

require o1 can see o2
require o1 can see o5
require o4 can see ego
require (distance from o2 to o1) <= 10 
require 10 <= (distance from o1 to ego) <= 20 
require 10 <= (distance from o4 to ego) <= 20 
require 10 <= (distance from o4 to o2) <= 20 
require 10 <= (distance from o4 to o3) <= 20 
require 20 <= (distance from o2 to ego) <= 50 
require 20 <= (distance from o3 to ego) <= 50 
require 20 <= (distance from o5 to o1) <= 50 
require 20 <= (distance from o5 to o2) <= 50 
require 20 <= (distance from o5 to o4) <= 50 

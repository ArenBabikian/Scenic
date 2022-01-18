param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASTORIGHT : [1, 4]; \
HASTORIGHT : [1, 5]; \
HASTORIGHT : [1, 0]; \
HASINFRONT : [5, 4]; \
HASTOLEFT : [2, 4]; \
HASBEHIND : [5, 3]; \
HASINFRONT : [5, 0]; \
HASTORIGHT : [0, 4]; \
HASTORIGHT : [1, 2]; \
HASINFRONT : [3, 4]; \
HASTOLEFT : [5, 2]; \
HASTORIGHT : [0, 3]; \
HASINFRONT : [3, 0]; \
HASTOLEFT : [2, 1]; \
HASTORIGHT : [3, 1]; \
HASTORIGHT : [0, 1]; \
HASTORIGHT : [4, 1]; \
HASINFRONT : [3, 5]; \
HASTORIGHT : [0, 5]; \
HASTOLEFT : [2, 5]; \
"
model scenic.simulators.carla.model

o4 = Car with color[0.265625, 0.625, 0.52734375]
o2 = Car left of o4 by Range(20, 50), with color[0.29296875, 0.46484375, 0.61328125]
o3 = Car behind o4 by Range(20, 50), with color[0.85546875, 0.74609375, 0.41015625]
ego = Car ahead of o4 by Range(10, 20), with color[0.734375, 0.72265625, 0.71484375]
o5 = Car behind o4 by Range(10, 20), with color[0.76953125, 0.6484375, 0.5234375]
o1 = Car right of o5 by Range(20, 50), with color[0.7578125, 0.359375, 0.33203125]

require o1 can see o3
require o2 can see o3
require o3 can see ego
require o3 can see o2
require o3 can see o4
require o3 can see o5
require o4 can see ego
require o5 can see ego
require o5 can see o4
require 10 <= (distance from o5 to o2) <= 20 
require 10 <= (distance from o5 to o3) <= 20 
require 20 <= (distance from o1 to ego) <= 50 
require 20 <= (distance from o2 to ego) <= 50 
require 20 <= (distance from o2 to o1) <= 50 
require 20 <= (distance from o3 to ego) <= 50 
require 20 <= (distance from o3 to o1) <= 50 
require 20 <= (distance from o3 to o2) <= 50 
require 20 <= (distance from o4 to o1) <= 50 
require 20 <= (distance from o5 to ego) <= 50 

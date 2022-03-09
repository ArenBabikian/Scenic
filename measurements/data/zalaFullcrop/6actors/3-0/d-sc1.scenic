param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASTOLEFT : [5, 2]; \
HASTOLEFT : [5, 3]; \
HASTOLEFT : [5, 0]; \
HASINFRONT : [1, 2]; \
HASINFRONT : [1, 3]; \
HASTOLEFT : [0, 2]; \
HASTORIGHT : [3, 2]; \
HASTOLEFT : [3, 0]; \
HASTOLEFT : [1, 4]; \
HASTORIGHT : [4, 1]; \
HASBEHIND : [2, 1]; \
HASTOLEFT : [2, 3]; \
HASTORIGHT : [0, 4]; \
HASTOLEFT : [3, 4]; \
HASTORIGHT : [0, 5]; \
HASTOLEFT : [2, 5]; \
HASTOLEFT : [4, 5]; \
"
model scenic.simulators.carla.model

o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
ego = Car left of o2 by Range(10, 20), with color[0.734375, 0.72265625, 0.71484375]
o3 = Car left of ego by Range(0, 10), with color[0.85546875, 0.74609375, 0.41015625]
o4 = Car left of o2 by Range(20, 50), with color[0.265625, 0.625, 0.52734375]
o1 = Car behind o3 by Range(20, 50), with color[0.7578125, 0.359375, 0.33203125]
o5 = Car left of o3 by Range(10, 20), with color[0.76953125, 0.6484375, 0.5234375]

require ego can see o1
require o1 can see ego
require o1 can see o2
require o1 can see o3
require o1 can see o5
require o2 can see o3
require o4 can see ego
require o4 can see o1
require o4 can see o2
require o4 can see o3
require o5 can see ego
require o5 can see o1
require o5 can see o4
require (distance from o3 to o2) <= 10 
require (distance from o5 to ego) <= 10 
require 10 <= (distance from o4 to ego) <= 20 
require 10 <= (distance from o5 to o2) <= 20 
require 10 <= (distance from o5 to o4) <= 20 
require 20 <= (distance from o1 to ego) <= 50 
require 20 <= (distance from o2 to o1) <= 50 
require 20 <= (distance from o4 to o1) <= 50 
require 20 <= (distance from o4 to o3) <= 50 
require 20 <= (distance from o5 to o1) <= 50 

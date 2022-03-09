param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASTOLEFT : [1, 5]; \
HASTOLEFT : [3, 5]; \
HASBEHIND : [1, 2]; \
HASTOLEFT : [0, 2]; \
HASTORIGHT : [4, 2]; \
HASTOLEFT : [1, 3]; \
HASTOLEFT : [1, 0]; \
HASINFRONT : [4, 3]; \
HASTORIGHT : [4, 1]; \
HASINFRONT : [3, 0]; \
HASINFRONT : [5, 2]; \
HASINFRONT : [5, 0]; \
HASTOLEFT : [3, 1]; \
HASTOLEFT : [5, 1]; \
HASBEHIND : [2, 1]; \
HASBEHIND : [0, 3]; \
HASTOLEFT : [1, 4]; \
HASINFRONT : [5, 4]; \
HASINFRONT : [3, 4]; \
"
model scenic.simulators.carla.model

o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
o5 = Car behind o2 by Range(20, 50), with color[0.76953125, 0.6484375, 0.5234375]
ego = Car right of o2 by Range(10, 20), with color[0.734375, 0.72265625, 0.71484375]
o3 = Car right of o5 by Range(20, 50), with color[0.85546875, 0.74609375, 0.41015625]
o1 = Car left of ego by Range(20, 50), with color[0.7578125, 0.359375, 0.33203125]
o4 = Car right of o2 by Range(10, 20), with color[0.265625, 0.625, 0.52734375]

require ego can see o4
require o1 can see o5
require o3 can see ego
require o3 can see o2
require o3 can see o4
require o4 can see ego
require o4 can see o3
require o4 can see o5
require o5 can see ego
require o5 can see o1
require o5 can see o2
require o5 can see o4
require (distance from o4 to ego) <= 10 
require 10 <= (distance from o5 to o1) <= 20 
require 20 <= (distance from o2 to o1) <= 50 
require 20 <= (distance from o3 to ego) <= 50 
require 20 <= (distance from o3 to o1) <= 50 
require 20 <= (distance from o3 to o2) <= 50 
require 20 <= (distance from o4 to o1) <= 50 
require 20 <= (distance from o4 to o3) <= 50 
require 20 <= (distance from o5 to ego) <= 50 
require 20 <= (distance from o5 to o4) <= 50 

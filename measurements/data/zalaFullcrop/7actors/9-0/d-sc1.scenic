param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASBEHIND : [6, 3]; \
HASINFRONT : [0, 3]; \
HASTORIGHT : [1, 3]; \
HASINFRONT : [0, 5]; \
HASBEHIND : [6, 2]; \
HASTOLEFT : [4, 5]; \
HASINFRONT : [0, 2]; \
HASBEHIND : [6, 1]; \
HASINFRONT : [5, 3]; \
HASINFRONT : [0, 6]; \
HASINFRONT : [4, 1]; \
HASBEHIND : [2, 0]; \
HASTORIGHT : [4, 0]; \
HASINFRONT : [5, 0]; \
HASBEHIND : [6, 0]; \
HASTORIGHT : [2, 1]; \
HASTOLEFT : [3, 2]; \
HASTOLEFT : [2, 4]; \
HASINFRONT : [5, 4]; \
HASTORIGHT : [1, 4]; \
HASBEHIND : [1, 6]; \
HASBEHIND : [3, 6]; \
HASINFRONT : [2, 6]; \
"
model scenic.simulators.carla.model

o3 = Car with color[0.85546875, 0.74609375, 0.41015625]
o5 = Car behind o3 by Range(10, 20), with color[0.76953125, 0.6484375, 0.5234375]
o2 = Car ahead of o5 by Range(10, 20), with color[0.29296875, 0.46484375, 0.61328125]
o1 = Car left of o3 by Range(10, 20), with color[0.7578125, 0.359375, 0.33203125]
o4 = Car right of o3 by Range(0, 10), with color[0.265625, 0.625, 0.52734375]
o6 = Car left of o4 by Range(20, 50), with color[0.1953125, 0.1953125, 0.1953125]
ego = Car ahead of o3 by Range(10, 20), with color[0.734375, 0.72265625, 0.71484375]

require ego can see o1
require ego can see o2
require ego can see o3
require ego can see o4
require ego can see o5
require ego can see o6
require o1 can see ego
require o2 can see o5
require o2 can see o6
require o3 can see ego
require o3 can see o4
require o4 can see o1
require o4 can see o2
require o4 can see o3
require o5 can see ego
require o5 can see o1
require o5 can see o2
require o5 can see o3
require o5 can see o4
require (distance from o3 to o2) <= 10 
require 10 <= (distance from o1 to ego) <= 20 
require 10 <= (distance from o2 to o1) <= 20 
require 10 <= (distance from o4 to ego) <= 20 
require 10 <= (distance from o4 to o1) <= 20 
require 10 <= (distance from o4 to o2) <= 20 
require 10 <= (distance from o6 to o5) <= 20 
require 20 <= (distance from o2 to ego) <= 50 
require 20 <= (distance from o5 to ego) <= 50 
require 20 <= (distance from o5 to o1) <= 50 
require 20 <= (distance from o5 to o4) <= 50 
require 20 <= (distance from o6 to ego) <= 50 
require 20 <= (distance from o6 to o1) <= 50 
require 20 <= (distance from o6 to o2) <= 50 
require 20 <= (distance from o6 to o3) <= 50 

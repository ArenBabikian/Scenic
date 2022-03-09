param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASINFRONT : [3, 2]; \
HASTOLEFT : [3, 5]; \
HASTOLEFT : [3, 0]; \
HASTORIGHT : [4, 5]; \
HASTORIGHT : [4, 1]; \
HASINFRONT : [6, 1]; \
HASTOLEFT : [6, 0]; \
HASTOLEFT : [5, 2]; \
HASTORIGHT : [1, 2]; \
HASINFRONT : [5, 0]; \
HASINFRONT : [3, 4]; \
HASTOLEFT : [5, 1]; \
HASTOLEFT : [0, 2]; \
HASTOLEFT : [3, 6]; \
HASTOLEFT : [5, 3]; \
HASINFRONT : [4, 3]; \
HASTOLEFT : [0, 3]; \
HASTORIGHT : [6, 3]; \
HASBEHIND : [2, 3]; \
HASTORIGHT : [1, 4]; \
HASTOLEFT : [5, 4]; \
HASTOLEFT : [0, 4]; \
HASTOLEFT : [2, 5]; \
HASBEHIND : [0, 5]; \
HASBEHIND : [1, 6]; \
HASINFRONT : [4, 6]; \
"
model scenic.simulators.carla.model

o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
ego = Car left of o2 by Range(20, 50), with color[0.734375, 0.72265625, 0.71484375]
o1 = Car left of o2 by Range(10, 20), with color[0.7578125, 0.359375, 0.33203125]
o5 = Car left of o1 by Range(20, 50), with color[0.76953125, 0.6484375, 0.5234375]
o4 = Car ahead of o2 by Range(0, 10), with color[0.265625, 0.625, 0.52734375]
o6 = Car left of ego by Range(10, 20), with color[0.1953125, 0.1953125, 0.1953125]
o3 = Car right of o1 by Range(20, 50), with color[0.85546875, 0.74609375, 0.41015625]

require o2 can see o4
require o3 can see o1
require o3 can see o2
require o3 can see o4
require o4 can see ego
require o4 can see o2
require o4 can see o3
require o4 can see o6
require o5 can see ego
require o5 can see o6
require o6 can see o1
require o6 can see o2
require o6 can see o3
require o6 can see o4
require o6 can see o5
require 10 <= (distance from o3 to o2) <= 20 
require 10 <= (distance from o4 to o1) <= 20 
require 20 <= (distance from o1 to ego) <= 50 
require 20 <= (distance from o3 to ego) <= 50 
require 20 <= (distance from o4 to ego) <= 50 
require 20 <= (distance from o4 to o3) <= 50 
require 20 <= (distance from o5 to ego) <= 50 
require 20 <= (distance from o5 to o2) <= 50 
require 20 <= (distance from o5 to o3) <= 50 
require 20 <= (distance from o5 to o4) <= 50 
require 20 <= (distance from o6 to o1) <= 50 
require 20 <= (distance from o6 to o2) <= 50 
require 20 <= (distance from o6 to o3) <= 50 
require 20 <= (distance from o6 to o4) <= 50 
require 20 <= (distance from o6 to o5) <= 50 

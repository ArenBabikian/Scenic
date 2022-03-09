param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASTOLEFT : [4, 1]; \
HASBEHIND : [0, 1]; \
HASINFRONT : [6, 1]; \
HASTORIGHT : [4, 5]; \
HASTORIGHT : [4, 2]; \
HASTOLEFT : [0, 2]; \
HASINFRONT : [4, 3]; \
HASINFRONT : [6, 3]; \
HASINFRONT : [5, 1]; \
HASINFRONT : [2, 1]; \
HASTORIGHT : [6, 0]; \
HASTORIGHT : [4, 0]; \
HASTOLEFT : [2, 5]; \
HASTORIGHT : [4, 6]; \
HASTOLEFT : [3, 5]; \
HASTORIGHT : [5, 0]; \
HASBEHIND : [1, 0]; \
HASTOLEFT : [2, 0]; \
HASBEHIND : [1, 2]; \
HASTORIGHT : [5, 2]; \
HASINFRONT : [5, 3]; \
HASTOLEFT : [3, 4]; \
HASINFRONT : [6, 4]; \
HASINFRONT : [2, 4]; \
HASBEHIND : [0, 4]; \
HASINFRONT : [5, 4]; \
HASTOLEFT : [2, 6]; \
HASTORIGHT : [0, 6]; \
HASTOLEFT : [3, 6]; \
"
model scenic.simulators.carla.model

o1 = Car with color[0.7578125, 0.359375, 0.33203125]
o5 = Car left of o1 by Range(20, 50), with color[0.76953125, 0.6484375, 0.5234375]
o3 = Car behind o1 by Range(10, 20), with color[0.85546875, 0.74609375, 0.41015625]
o2 = Car behind o3 by Range(20, 50), with color[0.29296875, 0.46484375, 0.61328125]
ego = Car behind o3 by Range(20, 50), with color[0.734375, 0.72265625, 0.71484375]
o6 = Car left of o1 by Range(20, 50), with color[0.1953125, 0.1953125, 0.1953125]
o4 = Car left of o1 by Range(10, 20), with color[0.265625, 0.625, 0.52734375]

require o2 can see o1
require o2 can see o3
require o2 can see o4
require o2 can see o5
require o3 can see o1
require o4 can see o2
require o4 can see o3
require o5 can see o1
require o5 can see o2
require o5 can see o3
require o5 can see o4
require o6 can see ego
require o6 can see o1
require o6 can see o2
require o6 can see o3
require o6 can see o4
require o6 can see o5
require (distance from o2 to ego) <= 10 
require (distance from o6 to o5) <= 10 
require 10 <= (distance from o4 to o3) <= 20 
require 20 <= (distance from o1 to ego) <= 50 
require 20 <= (distance from o2 to o1) <= 50 
require 20 <= (distance from o4 to ego) <= 50 
require 20 <= (distance from o4 to o2) <= 50 
require 20 <= (distance from o5 to ego) <= 50 
require 20 <= (distance from o5 to o2) <= 50 
require 20 <= (distance from o5 to o3) <= 50 
require 20 <= (distance from o5 to o4) <= 50 
require 20 <= (distance from o6 to ego) <= 50 
require 20 <= (distance from o6 to o2) <= 50 
require 20 <= (distance from o6 to o3) <= 50 
require 20 <= (distance from o6 to o4) <= 50 

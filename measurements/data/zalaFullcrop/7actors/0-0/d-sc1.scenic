param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASTOLEFT : [5, 0]; \
HASBEHIND : [5, 4]; \
HASBEHIND : [5, 6]; \
HASTOLEFT : [5, 3]; \
HASTOLEFT : [2, 0]; \
HASBEHIND : [2, 6]; \
HASBEHIND : [2, 4]; \
HASTOLEFT : [0, 6]; \
HASTOLEFT : [0, 4]; \
HASTOLEFT : [0, 3]; \
HASBEHIND : [3, 6]; \
HASTOLEFT : [5, 1]; \
HASBEHIND : [4, 6]; \
HASBEHIND : [2, 5]; \
HASINFRONT : [4, 3]; \
HASTOLEFT : [0, 1]; \
HASTOLEFT : [6, 0]; \
HASTORIGHT : [1, 0]; \
HASTOLEFT : [4, 0]; \
HASTOLEFT : [0, 2]; \
HASINFRONT : [6, 2]; \
HASINFRONT : [5, 2]; \
HASINFRONT : [6, 4]; \
HASTORIGHT : [3, 5]; \
HASTOLEFT : [0, 5]; \
HASINFRONT : [4, 5]; \
HASTOLEFT : [1, 5]; \
"
model scenic.simulators.carla.model

o1 = Car with color[0.7578125, 0.359375, 0.33203125]
o6 = Car with color[0.1953125, 0.1953125, 0.1953125]
o3 = Car ahead of o6 by Range(20, 50), with color[0.85546875, 0.74609375, 0.41015625]
o4 = Car behind o3 by Range(20, 50), with color[0.265625, 0.625, 0.52734375]
ego = Car left of o3 by Range(20, 50), with color[0.734375, 0.72265625, 0.71484375]
o5 = Car ahead of o6 by Range(20, 50), with color[0.76953125, 0.6484375, 0.5234375]
o2 = Car ahead of o4 by Range(20, 50), with color[0.29296875, 0.46484375, 0.61328125]

require o1 can see o4
require o1 can see o6
require o3 can see o2
require o4 can see o1
require o4 can see o2
require o4 can see o3
require o4 can see o5
require o5 can see o2
require o5 can see o3
require o6 can see o1
require o6 can see o2
require o6 can see o3
require o6 can see o4
require o6 can see o5
require (distance from o5 to o3) <= 10 
require (distance from o6 to o4) <= 10 
require 10 <= (distance from o3 to o1) <= 20 
require 10 <= (distance from o3 to o2) <= 20 
require 10 <= (distance from o4 to o1) <= 20 
require 10 <= (distance from o5 to o1) <= 20 
require 10 <= (distance from o5 to o2) <= 20 
require 20 <= (distance from o1 to ego) <= 50 
require 20 <= (distance from o2 to ego) <= 50 
require 20 <= (distance from o2 to o1) <= 50 
require 20 <= (distance from o4 to ego) <= 50 
require 20 <= (distance from o5 to ego) <= 50 
require 20 <= (distance from o5 to o4) <= 50 
require 20 <= (distance from o6 to ego) <= 50 
require 20 <= (distance from o6 to o1) <= 50 
require 20 <= (distance from o6 to o2) <= 50 

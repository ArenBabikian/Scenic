param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASTOLEFT : [0, 4]; \
HASTOLEFT : [3, 5]; \
HASTORIGHT : [3, 4]; \
HASINFRONT : [0, 5]; \
HASBEHIND : [6, 5]; \
HASTOLEFT : [2, 4]; \
HASBEHIND : [6, 1]; \
HASTOLEFT : [2, 5]; \
HASINFRONT : [3, 1]; \
HASTOLEFT : [0, 1]; \
HASTOLEFT : [3, 2]; \
HASINFRONT : [3, 6]; \
HASBEHIND : [0, 6]; \
HASINFRONT : [0, 2]; \
HASBEHIND : [5, 1]; \
HASTOLEFT : [4, 1]; \
HASTOLEFT : [0, 3]; \
HASBEHIND : [6, 2]; \
HASTOLEFT : [5, 4]; \
HASBEHIND : [2, 0]; \
HASTOLEFT : [4, 0]; \
HASBEHIND : [5, 0]; \
HASBEHIND : [6, 0]; \
HASTOLEFT : [3, 0]; \
HASTORIGHT : [5, 2]; \
HASTOLEFT : [5, 3]; \
HASTOLEFT : [2, 3]; \
HASBEHIND : [1, 3]; \
HASBEHIND : [6, 3]; \
HASTOLEFT : [4, 5]; \
HASBEHIND : [5, 6]; \
HASINFRONT : [4, 6]; \
HASINFRONT : [1, 6]; \
"
model scenic.simulators.carla.model

o1 = Car with color[0.7578125, 0.359375, 0.33203125]
o4 = Car right of o1 by Range(20, 50), with color[0.265625, 0.625, 0.52734375]
o5 = Car behind o1 by Range(10, 20), with color[0.76953125, 0.6484375, 0.5234375]
o2 = Car left of o4 by Range(20, 50), with color[0.29296875, 0.46484375, 0.61328125]
o6 = Car behind o2 by Range(20, 50), with color[0.1953125, 0.1953125, 0.1953125]
o3 = Car left of o4 by Range(20, 50), with color[0.85546875, 0.74609375, 0.41015625]
ego = Car left of o1 by Range(10, 20), with color[0.734375, 0.72265625, 0.71484375]

require ego can see o2
require ego can see o5
require o1 can see o6
require o3 can see o1
require o3 can see o6
require o4 can see o6
require (distance from o5 to o2) <= 10 
require 10 <= (distance from o2 to ego) <= 20 
require 10 <= (distance from o3 to ego) <= 20 
require 10 <= (distance from o3 to o1) <= 20 
require 10 <= (distance from o3 to o2) <= 20 
require 10 <= (distance from o5 to ego) <= 20 
require 10 <= (distance from o5 to o3) <= 20 
require 20 <= (distance from o2 to o1) <= 50 
require 20 <= (distance from o4 to ego) <= 50 
require 20 <= (distance from o5 to o4) <= 50 
require 20 <= (distance from o6 to ego) <= 50 
require 20 <= (distance from o6 to o1) <= 50 
require 20 <= (distance from o6 to o3) <= 50 
require 20 <= (distance from o6 to o4) <= 50 
require 20 <= (distance from o6 to o5) <= 50 

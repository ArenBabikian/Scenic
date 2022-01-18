param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASBEHIND : [3, 5]; \
HASBEHIND : [6, 5]; \
HASBEHIND : [4, 2]; \
HASBEHIND : [4, 1]; \
HASTOLEFT : [0, 1]; \
HASBEHIND : [6, 4]; \
HASBEHIND : [3, 4]; \
HASTOLEFT : [6, 0]; \
HASTOLEFT : [1, 2]; \
HASTORIGHT : [5, 2]; \
HASTOLEFT : [6, 3]; \
HASBEHIND : [4, 0]; \
HASTOLEFT : [1, 0]; \
HASTORIGHT : [2, 1]; \
HASBEHIND : [5, 3]; \
HASTOLEFT : [1, 3]; \
HASTOLEFT : [4, 3]; \
HASTORIGHT : [0, 3]; \
HASINFRONT : [2, 4]; \
HASINFRONT : [1, 4]; \
HASTOLEFT : [5, 4]; \
HASTOLEFT : [1, 6]; \
HASBEHIND : [5, 6]; \
HASTORIGHT : [0, 6]; \
HASTOLEFT : [2, 6]; \
HASTOLEFT : [4, 6]; \
"
model scenic.simulators.carla.model

o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
o5 = Car right of o2 by Range(0, 10), with color[0.76953125, 0.6484375, 0.5234375]
o1 = Car right of o5 by Range(0, 10), with color[0.7578125, 0.359375, 0.33203125]
ego = Car right of o5 by Range(10, 20), with color[0.734375, 0.72265625, 0.71484375]
o4 = Car behind ego by Range(20, 50), with color[0.265625, 0.625, 0.52734375]
o3 = Car left of o2 by Range(20, 50), with color[0.85546875, 0.74609375, 0.41015625]
o6 = Car right of o3 by Range(0, 10), with color[0.1953125, 0.1953125, 0.1953125]

require o1 can see o2
require o1 can see o4
require o1 can see o5
require o2 can see o1
require o2 can see o4
require o2 can see o5
require o3 can see o6
require (distance from o1 to ego) <= 10 
require (distance from o2 to ego) <= 10 
require (distance from o2 to o1) <= 10 
require 20 <= (distance from o3 to ego) <= 50 
require 20 <= (distance from o3 to o1) <= 50 
require 20 <= (distance from o4 to o1) <= 50 
require 20 <= (distance from o4 to o2) <= 50 
require 20 <= (distance from o4 to o3) <= 50 
require 20 <= (distance from o5 to o3) <= 50 
require 20 <= (distance from o5 to o4) <= 50 
require 20 <= (distance from o6 to ego) <= 50 
require 20 <= (distance from o6 to o1) <= 50 
require 20 <= (distance from o6 to o2) <= 50 
require 20 <= (distance from o6 to o4) <= 50 
require 20 <= (distance from o6 to o5) <= 50 

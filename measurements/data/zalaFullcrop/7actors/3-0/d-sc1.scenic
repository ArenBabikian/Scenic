param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASINFRONT : [4, 1]; \
HASTOLEFT : [0, 3]; \
HASINFRONT : [4, 3]; \
HASTOLEFT : [0, 1]; \
HASBEHIND : [6, 1]; \
HASINFRONT : [5, 1]; \
HASBEHIND : [2, 3]; \
HASTOLEFT : [5, 6]; \
HASINFRONT : [5, 2]; \
HASTORIGHT : [4, 6]; \
HASTOLEFT : [0, 2]; \
HASTORIGHT : [4, 0]; \
HASTOLEFT : [2, 6]; \
HASBEHIND : [1, 3]; \
HASINFRONT : [5, 4]; \
HASBEHIND : [6, 0]; \
HASTOLEFT : [2, 0]; \
HASTOLEFT : [1, 0]; \
HASBEHIND : [3, 2]; \
HASBEHIND : [6, 4]; \
HASBEHIND : [3, 4]; \
HASINFRONT : [1, 4]; \
HASTOLEFT : [0, 5]; \
HASBEHIND : [2, 5]; \
HASBEHIND : [1, 5]; \
HASTORIGHT : [3, 6]; \
"
model scenic.simulators.carla.model

o3 = Car with color[0.85546875, 0.74609375, 0.41015625]
o1 = Car behind o3 by Range(10, 20), with color[0.7578125, 0.359375, 0.33203125]
o6 = Car left of o1 by Range(20, 50), with color[0.1953125, 0.1953125, 0.1953125]
o2 = Car behind o6 by Range(20, 50), with color[0.29296875, 0.46484375, 0.61328125]
ego = Car behind o3 by Range(20, 50), with color[0.734375, 0.72265625, 0.71484375]
o4 = Car behind ego by Range(10, 20), with color[0.265625, 0.625, 0.52734375]
o5 = Car ahead of o4 by Range(20, 50), with color[0.76953125, 0.6484375, 0.5234375]

require ego can see o6
require o1 can see ego
require o1 can see o2
require o1 can see o4
require o2 can see o4
require o4 can see ego
require o4 can see o1
require o4 can see o2
require o4 can see o3
require o4 can see o5
require o5 can see ego
require o5 can see o1
require o5 can see o2
require o5 can see o4
require (distance from o5 to o1) <= 10 
require (distance from o5 to o3) <= 10 
require 10 <= (distance from o1 to ego) <= 20 
require 10 <= (distance from o2 to ego) <= 20 
require 10 <= (distance from o2 to o1) <= 20 
require 10 <= (distance from o4 to o2) <= 20 
require 10 <= (distance from o5 to o2) <= 20 
require 20 <= (distance from o3 to o2) <= 50 
require 20 <= (distance from o4 to o1) <= 50 
require 20 <= (distance from o4 to o3) <= 50 
require 20 <= (distance from o5 to ego) <= 50 
require 20 <= (distance from o6 to ego) <= 50 
require 20 <= (distance from o6 to o3) <= 50 
require 20 <= (distance from o6 to o4) <= 50 
require 20 <= (distance from o6 to o5) <= 50 

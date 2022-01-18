param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASTORIGHT : [1, 5]; \
HASINFRONT : [1, 3]; \
HASTOLEFT : [6, 5]; \
HASINFRONT : [0, 3]; \
HASTORIGHT : [0, 2]; \
HASTOLEFT : [5, 3]; \
HASTOLEFT : [5, 4]; \
HASTOLEFT : [1, 0]; \
HASINFRONT : [1, 6]; \
HASBEHIND : [3, 4]; \
HASTOLEFT : [5, 2]; \
HASTOLEFT : [2, 0]; \
HASTOLEFT : [5, 0]; \
HASTORIGHT : [0, 1]; \
HASINFRONT : [2, 1]; \
HASTORIGHT : [3, 1]; \
HASTOLEFT : [5, 1]; \
HASINFRONT : [4, 1]; \
HASINFRONT : [4, 5]; \
HASTORIGHT : [3, 5]; \
HASINFRONT : [5, 6]; \
"
model scenic.simulators.carla.model

o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
o4 = Car with color[0.265625, 0.625, 0.52734375]
o3 = Car ahead of o4 by Range(20, 50), with color[0.85546875, 0.74609375, 0.41015625]
o5 = Car ahead of o2 by Range(20, 50), with color[0.76953125, 0.6484375, 0.5234375]
ego = Car behind o3 by Range(10, 20), with color[0.734375, 0.72265625, 0.71484375]
o6 = Car ahead of ego by Range(20, 50), with color[0.1953125, 0.1953125, 0.1953125]
o1 = Car left of o6 by Range(20, 50), with color[0.7578125, 0.359375, 0.33203125]

require ego can see o3
require ego can see o5
require ego can see o6
require o1 can see o3
require o1 can see o6
require o2 can see o1
require o2 can see o3
require o2 can see o5
require o2 can see o6
require o3 can see o5
require o3 can see o6
require o4 can see ego
require o4 can see o1
require o4 can see o2
require o4 can see o3
require o4 can see o5
require o4 can see o6
require o5 can see o3
require o5 can see o6
require o6 can see ego
require o6 can see o1
require o6 can see o2
require o6 can see o3
require o6 can see o4
require (distance from o4 to o2) <= 10 
require 10 <= (distance from o1 to ego) <= 20 
require 10 <= (distance from o2 to ego) <= 20 
require 10 <= (distance from o2 to o1) <= 20 
require 10 <= (distance from o3 to o1) <= 20 
require 10 <= (distance from o4 to ego) <= 20 
require 10 <= (distance from o4 to o1) <= 20 
require 20 <= (distance from o3 to o2) <= 50 
require 20 <= (distance from o5 to ego) <= 50 
require 20 <= (distance from o5 to o1) <= 50 
require 20 <= (distance from o5 to o3) <= 50 
require 20 <= (distance from o5 to o4) <= 50 
require 20 <= (distance from o6 to o2) <= 50 
require 20 <= (distance from o6 to o3) <= 50 
require 20 <= (distance from o6 to o4) <= 50 
require 20 <= (distance from o6 to o5) <= 50 

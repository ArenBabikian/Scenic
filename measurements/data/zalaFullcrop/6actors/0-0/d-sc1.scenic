param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASINFRONT : [2, 0]; \
HASINFRONT : [2, 4]; \
HASINFRONT : [2, 3]; \
HASINFRONT : [2, 5]; \
HASINFRONT : [4, 0]; \
HASINFRONT : [1, 0]; \
HASBEHIND : [4, 3]; \
HASTOLEFT : [4, 5]; \
HASINFRONT : [3, 0]; \
HASTOLEFT : [5, 0]; \
HASINFRONT : [2, 1]; \
HASINFRONT : [5, 3]; \
HASBEHIND : [4, 1]; \
HASBEHIND : [0, 2]; \
HASBEHIND : [1, 2]; \
HASBEHIND : [4, 2]; \
HASBEHIND : [3, 2]; \
HASINFRONT : [1, 4]; \
HASINFRONT : [3, 4]; \
HASBEHIND : [0, 4]; \
HASINFRONT : [3, 5]; \
"
model scenic.simulators.carla.model

ego = Car with color[0.734375, 0.72265625, 0.71484375]
o1 = Car behind ego by Range(20, 50), with color[0.7578125, 0.359375, 0.33203125]
o3 = Car behind ego by Range(20, 50), with color[0.85546875, 0.74609375, 0.41015625]
o5 = Car left of ego by Range(10, 20), with color[0.76953125, 0.6484375, 0.5234375]
o4 = Car left of o5 by Range(10, 20), with color[0.265625, 0.625, 0.52734375]
o2 = Car ahead of o5 by Range(20, 50), with color[0.29296875, 0.46484375, 0.61328125]

require o1 can see ego
require o1 can see o4
require o1 can see o5
require o2 can see ego
require o2 can see o1
require o2 can see o3
require o2 can see o4
require o2 can see o5
require o3 can see ego
require o3 can see o1
require o3 can see o4
require o3 can see o5
require o4 can see ego
require o5 can see o1
require o5 can see o2
require o5 can see o3
require (distance from o4 to o1) <= 10 
require 10 <= (distance from o3 to o1) <= 20 
require 10 <= (distance from o3 to o2) <= 20 
require 10 <= (distance from o4 to ego) <= 20 
require 20 <= (distance from o2 to ego) <= 50 
require 20 <= (distance from o2 to o1) <= 50 
require 20 <= (distance from o4 to o2) <= 50 
require 20 <= (distance from o4 to o3) <= 50 
require 20 <= (distance from o5 to o1) <= 50 
require 20 <= (distance from o5 to o3) <= 50 

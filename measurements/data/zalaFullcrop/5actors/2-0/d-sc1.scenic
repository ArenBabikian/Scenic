param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASINFRONT : [4, 1]; \
HASINFRONT : [3, 1]; \
HASTOLEFT : [2, 0]; \
HASBEHIND : [1, 0]; \
HASTOLEFT : [2, 1]; \
HASTORIGHT : [1, 2]; \
HASBEHIND : [0, 3]; \
HASBEHIND : [1, 3]; \
HASBEHIND : [2, 4]; \
HASTORIGHT : [3, 4]; \
HASTORIGHT : [1, 4]; \
"
model scenic.simulators.carla.model

ego = Car with color[0.734375, 0.72265625, 0.71484375]
o1 = Car behind ego by Range(10, 20), with color[0.7578125, 0.359375, 0.33203125]
o2 = Car behind ego by Range(20, 50), with color[0.29296875, 0.46484375, 0.61328125]
o3 = Car left of o2 by Range(20, 50), with color[0.85546875, 0.74609375, 0.41015625]
o4 = Car left of ego by Range(20, 50), with color[0.265625, 0.625, 0.52734375]

require o3 can see o1
require o3 can see o2
require o4 can see ego
require o4 can see o1
require o4 can see o2
require o4 can see o3
require (distance from o3 to ego) <= 10 
require (distance from o3 to o1) <= 10 
require 10 <= (distance from o4 to o2) <= 20 
require 20 <= (distance from o2 to o1) <= 50 
require 20 <= (distance from o4 to o1) <= 50 
require 20 <= (distance from o4 to o3) <= 50 

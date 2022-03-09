param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASBEHIND : [0, 4]; \
HASINFRONT : [1, 4]; \
HASTOLEFT : [1, 3]; \
HASINFRONT : [2, 4]; \
HASINFRONT : [0, 3]; \
HASTOLEFT : [2, 0]; \
HASBEHIND : [2, 1]; \
HASTOLEFT : [1, 0]; \
HASBEHIND : [3, 4]; \
HASBEHIND : [3, 0]; \
HASTOLEFT : [3, 1]; \
HASBEHIND : [4, 1]; \
HASTOLEFT : [0, 2]; \
HASINFRONT : [1, 2]; \
"
model scenic.simulators.carla.model

o4 = Car with color[0.265625, 0.625, 0.52734375]
o3 = Car behind o4 by Range(20, 50), with color[0.85546875, 0.74609375, 0.41015625]
ego = Car behind o4 by Range(20, 50), with color[0.734375, 0.72265625, 0.71484375]
o1 = Car left of ego by Range(20, 50), with color[0.7578125, 0.359375, 0.33203125]
o2 = Car behind o4 by Range(10, 20), with color[0.29296875, 0.46484375, 0.61328125]

require ego can see o1
require ego can see o3
require o1 can see ego
require o1 can see o2
require o1 can see o4
require o2 can see o4
require 10 <= (distance from o2 to ego) <= 20 
require 10 <= (distance from o3 to ego) <= 20 
require 10 <= (distance from o3 to o1) <= 20 
require 20 <= (distance from o2 to o1) <= 50 
require 20 <= (distance from o3 to o2) <= 50 
require 20 <= (distance from o4 to o1) <= 50 

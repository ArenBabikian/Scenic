param map = localPath('/usr/src/app/maps/zalaFullcrop.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASBEHIND : [1, 0]; \
HASBEHIND : [3, 0]; \
HASTOLEFT : [1, 2]; \
HASBEHIND : [3, 2]; \
HASINFRONT : [2, 0]; \
HASBEHIND : [1, 3]; \
HASBEHIND : [0, 1]; \
HASTOLEFT : [2, 1]; \
HASINFRONT : [0, 3]; \
"
model scenic.simulators.carla.model

ego = Car with color[0.734375, 0.72265625, 0.71484375]
o2 = Car behind ego by Range(10, 20), with color[0.29296875, 0.46484375, 0.61328125]
o3 = Car ahead of o2 by Range(10, 20), with color[0.85546875, 0.74609375, 0.41015625]
o1 = Car behind o3 by Range(10, 20), with color[0.7578125, 0.359375, 0.33203125]

require ego can see o3
require o1 can see o2
require o2 can see ego
require o2 can see o1
require o2 can see o3
require (distance from o2 to o1) <= 10 
require (distance from o3 to ego) <= 10 
require 10 <= (distance from o1 to ego) <= 20 

param map = localPath('/usr/src/app/maps/town02.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASINFRONT : [2, 1]; \
HASINFRONT : [3, 1]; \
HASBEHIND : [3, 2]; \
HASTOLEFT : [1, 0]; \
HASTORIGHT : [0, 2]; \
HASBEHIND : [1, 3]; \
HASINFRONT : [2, 3]; \
"
model scenic.simulators.carla.model

ego = Car with color[0.734375, 0.72265625, 0.71484375]
o1 = Car ahead of ego by Range(0, 10), with color[0.7578125, 0.359375, 0.33203125]
o2 = Car behind o1 by Range(20, 50), with color[0.29296875, 0.46484375, 0.61328125]
o3 = Car right of ego by Range(10, 20), with color[0.85546875, 0.74609375, 0.41015625]

require ego can see o1
require o2 can see ego
require o2 can see o1
require o2 can see o3
require o3 can see ego
require o3 can see o1
require (distance from o3 to o2) <= 10 
require 10 <= (distance from o3 to o1) <= 20 
require 20 <= (distance from o2 to ego) <= 50 

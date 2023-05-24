param map = localPath('/usr/src/app/maps/town02.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASBEHIND : [1, 2]; \
HASINFRONT : [1, 3]; \
HASINFRONT : [0, 2]; \
HASTOLEFT : [1, 0]; \
HASBEHIND : [2, 3]; \
HASBEHIND : [3, 1]; \
HASBEHIND : [2, 1]; \
"
model scenic.simulators.carla.model

o3 = Car with color[0.85546875, 0.74609375, 0.41015625]
o2 = Car behind o3 by Range(10, 20), with color[0.29296875, 0.46484375, 0.61328125]
ego = Car behind o2 by Range(10, 20), with color[0.734375, 0.72265625, 0.71484375]
o1 = Car left of ego by Range(0, 10), with color[0.7578125, 0.359375, 0.33203125]

require ego can see o1
require ego can see o2
require o1 can see ego
require o1 can see o3
require (distance from o2 to o1) <= 10 
require (distance from o3 to ego) <= 10 
require 10 <= (distance from o3 to o1) <= 20 

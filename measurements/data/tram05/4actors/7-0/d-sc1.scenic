param map = localPath('/usr/src/app/maps/tram05.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASINFRONT : [1, 3]; \
HASINFRONT : [1, 0]; \
HASINFRONT : [3, 0]; \
HASTOLEFT : [1, 2]; \
HASBEHIND : [0, 1]; \
HASBEHIND : [3, 1]; \
"
model scenic.simulators.carla.model

ego = Car with color[0.734375, 0.72265625, 0.71484375]
o2 = Car behind ego by Range(10, 20), with color[0.29296875, 0.46484375, 0.61328125]
o3 = Car behind ego by Range(0, 10), with color[0.85546875, 0.74609375, 0.41015625]
o1 = Car left of o2 by Range(0, 10), with color[0.7578125, 0.359375, 0.33203125]

require o1 can see ego
require o1 can see o3
require o3 can see ego
require (distance from o3 to o1) <= 10 
require 10 <= (distance from o1 to ego) <= 20 
require 10 <= (distance from o3 to o2) <= 20 

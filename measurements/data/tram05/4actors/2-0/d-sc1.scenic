param map = localPath('/usr/src/app/maps/tram05.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASTORIGHT : [3, 2]; \
HASTOLEFT : [1, 2]; \
HASBEHIND : [1, 0]; \
HASTORIGHT : [1, 3]; \
HASBEHIND : [0, 2]; \
HASTORIGHT : [3, 1]; \
HASTOLEFT : [2, 1]; \
HASTOLEFT : [2, 3]; \
"
model scenic.simulators.carla.model

o2 = Car with color[0.29296875, 0.46484375, 0.61328125]
ego = Car ahead of o2 by Range(10, 20), with color[0.734375, 0.72265625, 0.71484375]
o3 = Car left of ego by Range(10, 20), with color[0.85546875, 0.74609375, 0.41015625]
o1 = Car behind ego by Range(10, 20), with color[0.7578125, 0.359375, 0.33203125]

require o2 can see ego
require o3 can see ego
require (distance from o2 to o1) <= 10 
require 10 <= (distance from o3 to o1) <= 20 
require 10 <= (distance from o3 to o2) <= 20 

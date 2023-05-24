param map = localPath('/usr/src/app/maps/town02.xodr')
# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASTORIGHT : [0, 1]; \
HASTOLEFT : [2, 1]; \
HASTOLEFT : [2, 0]; \
"
model scenic.simulators.carla.model

o1 = Car with color[0.7578125, 0.359375, 0.33203125]
o2 = Car behind o1 by Range(10, 20), with color[0.29296875, 0.46484375, 0.61328125]
ego = Car behind o1 by Range(10, 20), with color[0.734375, 0.72265625, 0.71484375]

require ego can see o2
require (distance from o2 to ego) <= 10 

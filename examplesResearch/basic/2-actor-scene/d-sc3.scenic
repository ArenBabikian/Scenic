# The original abstract scenario is IRREPRESENTIBLE.
# Thus we removed these constraints to make it representible
param constraints = " \
HASTORIGHT : [0, 1]; \
"
model scenic.simulators.carla.model

o1 = Car with color[0.7578125, 0.359375, 0.33203125]
ego = Car in SectorRegion(o1, 50, o1.heading, math.radians(22.5)).intersect(CircularRegion(o1, 20)).difference(CircularRegion(o1, 10)), with color[0.734375, 0.72265625, 0.71484375]

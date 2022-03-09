param map = localPath('C:/git/CarlaScenarioGen/Interface/maps/tram05.xodr')
model scenic.simulators.carla.model

o1 = Car  with color[0.7578125, 0.359375, 0.33203125]
ego = Car ahead of o1 by Range(0, 10), with color[0.734375, 0.72265625, 0.71484375]

o2 = Car left of ego by Range(0, 10), with color[0.29296875, 0.46484375, 0.61328125]

#require 20 <= (distance from ego to o1) <= 50 
#require ego can see o1
#require 20 <= (distance from ego to o2) <= 50 
#require ego can see o2
#require o2 can see ego
#require (distance from o1 to o2) <= 10 

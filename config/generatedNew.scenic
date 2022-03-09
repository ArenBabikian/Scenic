param map = localPath('C:/git/CarlaScenarioGen/Interface/maps/tram05.xodr')
# param carla_map = 'Town02'
param constraints = " \
					ONROAD : [0, -1]; \
					ONROAD : [1, -1]; \
					ONROAD : [2, -1]; \
					ONROAD : [3, -1]; \
					NOCOLLISION : [0, 1]; \
					NOCOLLISION : [0, 2]; \
					NOCOLLISION : [0, 3]; \
					NOCOLLISION : [1, 2]; \
					NOCOLLISION : [1, 3]; \
					NOCOLLISION : [2, 3]; \
					CANSEE : [0, 1]; \
					CANSEE : [0, 2]; \
					CANSEE : [0, 3]; \
					DISTMED : [3, 1]; \
					DISTMED : [3, 2]; \
					HASINFRONT : [1, 3]; \
							"
model scenic.simulators.carla.model

ego = Car \
	with color[0/256, 0/256, 0/256] # Black
a_1 = Car \
	with color[188/256, 185/256, 183/256] # Silver
a_2 = Car \
	with color[194/256, 92/256, 85/256] # red
a_3 = Car \
	with color [75/256, 119/256, 157/256] # blue


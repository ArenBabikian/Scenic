param map = localPath('C:/git/Scenic/maps/tram05.xodr')
param weather = 'ClearNoon'
model scenic.simulators.carla.model

#egoPos = (-36.080394843173636 @ 12.223735036355448) # COLLIDES
egoPos = (-27.365169525146484 @ 5.752239227294922) # DOES NOT COLLIDE
o2Pos = (-47.898719787597656 @ 15.695693016052246)
o1Pos = (-48.13116455078125 @ 18.38742446899414)

ego = Car at egoPos, with blueprint "vehicle.audi.etron"
o2 = Car at o2Pos, with blueprint "vehicle.lincoln.mkz_2017"
o1 = Car at o1Pos, with blueprint "vehicle.lincoln.mkz_2017"
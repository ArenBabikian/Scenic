param map = localPath('C:/git/Scenic/maps/tram05.xodr')
param weather = 'ClearNoon'
model scenic.simulators.carla.model

param dyn_constraints = " \
SP_SLOW : [0, -1]; \
BE_SCENIC : [0, -1]; \
"

egoPos = (-27.365169525146484 @ 5.752239227294922)
ego = Car at egoPos, with blueprint "vehicle.audi.etron", with behavior FollowLaneBehavior(target_speed=2)
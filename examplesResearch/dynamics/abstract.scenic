param constraints = " \ONROAD : [0, -1]; \
ONROAD : [1, -1]; \
ONROAD : [2, -1]; \
NOCOLLISION : [0, 1]; \
NOCOLLISION : [1, 2]; \
NOCOLLISION : [2, 0]; \
DISTCLOSE : [1, 2]; \
HASTOLEFT : [2, 1]; \
HASTORIGHT : [1, 2]; \
DISTMED : [2, 0]; \
HASBEHIND : [0, 2]; \
HASINFRONT : [2, 0]; \
"
# RESULTS IN COLISION SIDE-BY-SIDE
# 0 is ego, 1 will cut on front of 0, 2 is the guy behind

param dyn_constraints = " \
SP_SLOW : [0, -1]; \
SP_FAST : [1, -1]; \
SP_NONE : [2, -1]; \
BE_SCENIC : [0, -1]; \
BE_SCENIC : [1, -1]; \
BE_NONE : [2, -1]; \
"

model scenic.simulators.carla.model

behavior OneBehavior():
    current_lane = network.laneAt(self)
    try:
        #do AccelerateForwardBehavior()
        do FollowLaneBehavior(30)

    interrupt when (distance from self.position to ego.position) <= 5:
        current_laneSection = network.laneSectionAt(self)
        rightLaneSec = current_laneSection.laneToRight
        do LaneChangeBehavior(rightLaneSec, is_oppositeTraffic=False, target_speed=30)

ego = Car with color[0.7578125, 0.359375, 0.33203125], with blueprint "vehicle.audi.etron", with behavior FollowLaneBehavior(2)
o1 = Car with color[0.734375, 0.72265625, 0.71484375], with blueprint "vehicle.lincoln.mkz_2017", with behavior OneBehavior()
o2 = Car with color[0.734375, 0.72265625, 0.71484375], with blueprint "vehicle.lincoln.mkz_2017"


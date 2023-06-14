param map = localPath('C:/git/Scenic/maps/tram05.xodr')
param weather = 'ClearNoon'
model scenic.simulators.carla.model

param dyn_constraints = " \
SP_SLOW : [0, -1]; \
SP_FAST : [1, -1]; \
SP_NONE : [2, -1]; \
BE_SCENIC : [0, -1]; \
BE_SCENIC : [1, -1]; \
BE_SCENIC : [2, -1]; \
"

IDLETIME = 200

behavior delayedBehavior(beh):
    try:
        #take SetReverseAction(True)
        while simulation().currentTime < IDLETIME:
            wait
        do FollowLaneBehavior(3)
    interrupt when simulation().currentTime > 175+IDLETIME:
        do beh

behavior stopWhenSee(obj, spd=2):
    try:
        do FollowLaneBehavior(spd)
    interrupt when self can see obj:
        take SetThrottleAction(0), SetBrakeAction(1)

behavior OneBehavior(spd):
    current_lane = network.laneAt(self)
    try:
        do FollowLaneBehavior(spd)

    #interrupt when (distance from self.position to o1.position) > 3:
    interrupt when not withinDistanceToAnyCars(self, 3):
        current_laneSection = network.laneSectionAt(self)
        rightLaneSec = current_laneSection.laneToRight
        do LaneChangeBehavior(rightLaneSec, is_oppositeTraffic=False, target_speed=3)

behavior AvoidColl(spd=25, thresh=10):
    try:
        do FollowLaneBehavior(target_speed=spd)
    interrupt when withinDistanceToAnyCars(self, thresh):
        take SetThrottleAction(0), SetBrakeAction(0)

behavior no():
    take SetThrottleAction(0), SetBrakeAction(0)

# ######################
# WORKING WITH 175 DELAY
# ######################
#egoPos = (-36.080394843173636 @ 12.223735036355448) # COLLIDES
egoPos = (-27.365169525146484 @ 5.752239227294922) # DOES NOT COLLIDE
o2Pos = (-47.898719787597656 @ 15.695693016052246)
o1Pos = (-48.13116455078125 @ 18.38742446899414)

ego = Car at egoPos, with blueprint "vehicle.audi.etron", with behavior delayedBehavior(AvoidColl(spd=2, thresh=20))
o2 = Car at o2Pos, with blueprint "vehicle.lincoln.mkz_2017", with behavior delayedBehavior(OneBehavior(spd=4))
o1 = Car at o1Pos, with blueprint "vehicle.lincoln.mkz_2017", with behavior delayedBehavior(stopWhenSee(obj=o2, spd=2))
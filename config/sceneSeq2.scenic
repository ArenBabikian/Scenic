param map = localPath('../maps/CARLA/Town10HD.xodr')
# param carla_map = 'Town01'
param render = 1
model scenic.domains.driving.model

behavior egoBehavior(other):
    # while self can see other:
    #     try:
    #         do FollowLaneBehavior(target_speed=3)
    #     # interrupt when self.distanceToClosest(Object) < 15:
    #     interrupt when (distance from self.position to other.position) < 15:
    #         print("changing Lanes")
    #         require self.laneSection.adjacentLanes
    #         do LaneChangeBehavior(Uniform(*self.laneSection.adjacentLanes))
    #         # do CollisionAvoidance()
    #     except:   # FollowLaneBehavior has failed
    #         print("ego exception")
    # while True:
    #     take SetThrottleAction(0.0), SetBrakeAction(1.0)  

    require self.laneSection.adjacentLanes
    
    l = Uniform(*self.laneSection.adjacentLanes)
    do LaneChangeBehavior(l)
    print("lane: changed")
    wait
    # do FollowLaneBehavior(2, laneToFollow=l)


    # # while (distance from self to car1) > 15:
    # # while not withinDistanceToObjsInLane(self, 15):
    # # while not withinDistanceToAnyObjs(self, 35):
    # while self.distanceToClosest(Car) > 35 :
    #     # do DriveAvoidingCollisions(avoidance_threshold=10)
    #     do FollowLaneBehavior(target_speed=3)
    # # take SetBrakeAction(1)
    # print("Slowed Down")
    # for i in range(100):
    #     do LaneChangeBehavior(Uniform(*self.laneSection.adjacentLanes))
    # print("Lane Change Done")
    # terminate



behavior carBehavior():

    # while True:
    #     try:
    #         # do ConstantThrottleBehavior(0.0)
    #         take SetThrottleAction(0.0), SetBrakeAction(1.0)
    #         # do FollowLaneBehavior(target_speed=1)
    #     interrupt when self.distanceToClosest(Object) < 15:
    do FollowLaneBehavior(target_speed=10, laneToFollow=self.lane)
        #     # require self.laneSection.adjacentLanes
        #     # do LaneChangeBehavior(Uniform(*self.laneSection.adjacentLanes))
        #     # do CollisionAvoidance()
        # except:   # FollowLaneBehavior has failed
        #     print("car exception")

ladj = [l for l in network.laneSections if l.adjacentLanes]
r = Uniform(*ladj)
pt = OrientedPoint in r.centerline


# p1 = DrivingObject following roadDirection from pt for Range(40, 50)
p1 = OrientedPoint following roadDirection from pt for Range(15, 20)
# laneOfP1 = [l for l in network.lanes if pt in l]
# rCenter = Uniform(*laneOfP1)
# pCenter = OrientedPoint in rCenter.centerline
# p1 = Lane ahead of pt by Range(40, 50)
# r1 = DrivingObject at p1
car1 = Car at p1,
        with carBehavior()
require car1.laneSection.adjacentLanes

ego = Car at pt,
        with behavior egoBehavior(car1)

require always not ego in intersection

monitor StopAfterInteraction:
	for i in range(300):
		wait
	# while car1 behind ego:
	# 	wait
	# for i in range(25):
	# 	wait
	terminate


# print([item.id for item in network.roads])
# print([item for item in network.crossings])

# roads_with_id = [item for item in network.roads if item.id == 1]
# print(roads_with_id)

# select_road = roads_with_id[0]
# select_lane = Uniform(*select_road.lanes)
# ego = Car behind select_lane.orientation

# crossing = Uniform(*network.crossings)
# Pedestrian on crossing

# right_sidewalk = network.laneGroupAt(ego)._sidewalk

# Pedestrian on visible right_sidewalk

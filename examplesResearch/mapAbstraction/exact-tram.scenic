param map = localPath('/home/aren/git/Scenic/maps/tram05.xodr')
param map_options = dict(useCache=False,writeCache=False, fill_intersections=False, segmentation_len=5, ref_points=30, tolerance=0.05)
model scenic.simulators.carla.model

param constraints = " COLLIDESATMANEUVER : [0, is_right]; \
"
#ego = Car at (-94.48527750309131 @ -29.886284580468843), with color[0.7578125, 0.359375, 0.33203125]
#a2 = Car at (-47.98412655809195 @ -14.291086036096143), with color[0.7578125, 0.359375, 0.33203125]

ego = Car at (76 @ -70), with color[0.7578125, 0.359375, 0.33203125]
a2 = Car at (-97 @ -28), with color[0.7578125, 0.359375, 0.33203125]

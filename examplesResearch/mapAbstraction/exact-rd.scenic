param map = localPath('/home/aren/git/Scenic/maps/town05.xodr')
param map_options = dict(useCache=True,writeCache=True, fill_intersections=False, segmentation_len=8, ref_points=20, tolerance=0.05)
model scenic.simulators.carla.model


param constraints = " COLLIDESATMANEUVER : [0, is_right]; \
"
#ego = Car at (31.373358262850388 @ 46.9124742511828), with color[0.7578125, 0.359375, 0.33203125]

# ego = Car at (24.100554488595897 @ -16.609791671100872)

ego = Car at (-15.19555449736197 @ -3.6007185547464475), with color[0.7578125, 0.359375, 0.33203125]
a1 = Car at (30.44413632725769 @ -20.90064242195674), with color[0.7578125, 0.359375, 0.33203125]

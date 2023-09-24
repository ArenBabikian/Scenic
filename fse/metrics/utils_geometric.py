


def closestDistanceBetweenRectangles(rectReg1, rectReg2):

    # The shortest distance must necessarily involve at least 1 corner
    # unless the rectangles are intersecting, which shouldnt happen in our case
    o1_polygon = rectReg1.polygon
    o2_polygon = rectReg2.polygon

    da = o1_polygon.distance(o2_polygon)
    db = o2_polygon.distance(o1_polygon)
    assert da == db
    return da
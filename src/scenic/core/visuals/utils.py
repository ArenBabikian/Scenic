
def clean_fig(plt):
    plt.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False, labelbottom=False, labelleft=False)
    plt.box(False)
    plt.margins(0, 0)
    plt.tight_layout(pad=0)


def show_network_alt(network, plt):
        colors = {'walk' : '#00A0FF',
                  'shoulder' : '#606060',
                  'road' : '#FF0000',
                  'intersection' : '#00FF00',
                  'cl' : '#A0A0A0'}
        grey = '#808080'
        # network.walkableRegion.show(plt, style='-', color='#00A0FF')
        # network.shoulderRegion.show(plt, style='-', color='#606060')
        network.shoulderRegion.show(plt, style='-', color=grey)
        for road in network.roads:
            road.show(plt, style='-', color=grey)
            for lane in road.lanes:     # will loop only over lanes of main roads
                lane.leftEdge.show(plt, style='--', color=grey)
                lane.rightEdge.show(plt, style='--', color=grey)

                # # Draw arrows indicating road direction
                # if lane.centerline.length >= 10:
                #     pts = lane.centerline.equallySpacedPoints(5)
                # else:
                #     pts = [lane.centerline.pointAlongBy(0.5, normalized=True)]
                # hs = [lane.centerline.orientation[pt] for pt in pts]
                # x, y = zip(*pts)
                # u = [math.cos(h + (math.pi/2)) for h in hs]
                # v = [math.sin(h + (math.pi/2)) for h in hs]
                # plt.quiver(x, y, u, v,
                #            pivot='middle', headlength=4.5,
                #            scale=0.06, units='dots', color='#A0A0A0')
        # for lane in network.lanes:     # draw centerlines of all lanes (including connecting)
        #     lane.centerline.show(plt, style=':', color='#A0A0A0')

        # network.intersectionRegion.show(plt, style='g')
        network.intersectionRegion.show(plt, style=grey)
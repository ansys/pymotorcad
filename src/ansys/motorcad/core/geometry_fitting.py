from ansys.motorcad.core.geometry import Arc, Coordinate, Line
from math import dist, atan2, pi, sqrt, sin, cos
import ezdxf

def orientation(c1, c2, c3):
    # to find the orientation of three coordinates
    val = (float(c2.y - c1.y) * (c3.x - c2.x)) - \
          (float(c2.x - c1.x) * (c3.y - c2.y))
    if val > 0:
        # Clockwise orientation
        return 1
    elif val < 0:
        # Counterclockwise orientation
        return 2
    else:
        # Collinear orientation
        return 0

def coordinatestoarc(c1, c2, c3):

    midX1 = (c1.x + c2.x) / 2
    midY1 = (c1.y + c2.y) / 2

    # avoid divide by zero errors in case of vertical lines
    if (c2.x - c1.x) == 0:
        slope1 = 0
    else:
        slope1 = (c2.y - c1.y) / (c2.x - c1.x)

    if (c3.x - c2.x) == 0:
        slope2 = 0
    else:
        slope2 = (c3.y - c2.y) / (c3.x - c2.x)

    midX2 = (c2.x + c3.x) / 2
    midY2 = (c2.y + c3.y) / 2

    if slope1 != 0 and slope2 != 0 and slope1 != slope2:

        perpslope1 = -1 / slope1
        perpslope2 = -1 / slope2

        xintersect = (midY1 - midY2 + perpslope2 * midX2 - perpslope1 * midX1) / (perpslope2 - perpslope1)
        yintersect = perpslope1 * (xintersect - midX1) + midY1

    elif slope1==slope2:
        #lines are parallel so no point of intersection
        return None

    elif slope1==0 and slope2==0 or slope1==slope2:
        #three points are on a straight line, no arc is possible
        return None

    elif slope1 == 0:
        # if line 1 is either vertical or horizontal
        if (c2.x - c1.x) == 0:
            yintersect = midY1
            perpslope2 = -1 / slope2
            xintersect = ((yintersect - midY2) / perpslope2) + midX2
        else:
            xintersect = midX1
            perpslope2 = -1 / slope2
            yintersect = perpslope2 * (xintersect - midX2) + midY2

    elif slope2 == 0:
        # if line 2 is either vertical or horizontal
        if (c3.x - c2.x) == 0:
            yintersect = midY2
            perpslope1 = -1 / slope1
            xintersect = ((yintersect - midY1) / perpslope1) + midX1
        else:
            xintersect = midX2
            perpslope1 = -1 / slope1
            yintersect = perpslope1 * (xintersect - midX1) + midY1

    radius = dist([c1.x, c1.y], [xintersect, yintersect])

    coord_centre = Coordinate(xintersect, yintersect)

    arcout = Arc(c1, c3, coord_centre, radius)

    return arcout

def checkllineerror(c_xy, slope, b, tolerance):

    errflag = False

    for xy in c_xy:
        ycalc = slope * xy.x + b
        yarray = abs(xy.y - ycalc)
        if (yarray > tolerance):
            errflag = True

    return errflag

def checkarcerror(c_xy, c_x0y0, r, tolerance):

    errflag = False

    for i in range(len(c_xy)):
        rcalc = sqrt((c_xy[i].x - c_x0y0.x) ** 2 + (c_xy[i].y - c_x0y0.y) ** 2)

        rerror = abs(r - rcalc)

        if rerror > tolerance:
            errflag = True


    return errflag

def returnentitylist(xypoints, linetolerance, arctolerance):

    #xypoints is a list of ordered co-ordinates

    newentitylist = []
    currentindex = 0
    xydynamiclist = xypoints.copy()

    while len(xydynamiclist) > 2:

        # need to consider sharp angle case where two separate line entities are required to represent 3 points
        # this could potentially be handled by a maximum arc angle limit
        linesegments = 1
        arcsegments = 1
        arcentitycomplete = False
        lineentitycomplete = False

        while lineentitycomplete is False:
            linesegments = linesegments + 1

            #loops through extending line until the tolerance is reached
            if len(xydynamiclist) >= linesegments + 1:
                startpoint = xypoints[currentindex]
                endpoint = xypoints[currentindex + linesegments]

                line_master = Line(startpoint, endpoint)
                slope = line_master.gradient
                b = startpoint.y - slope * startpoint.x
                lineentitycomplete = checkllineerror(xypoints[currentindex:currentindex + linesegments + 1], slope,
                                                     b, linetolerance)
            else:
                lineentitycomplete = True

        if lineentitycomplete:
            linesegments = linesegments - 1

        while arcentitycomplete is False:
            #loops through extending the arc until the tolerance is reached
            arcsegments = arcsegments + 1

            if len(xydynamiclist) >= arcsegments + 1:
                startpoint = xypoints[currentindex]
                endpoint = xypoints[currentindex + arcsegments]
                midpoint = xypoints[currentindex + round(arcsegments / 2)]

                arc_master = coordinatestoarc(startpoint, midpoint, endpoint)

                if arc_master==None:
                    arcentitycomplete = True
                else:
                    arcentitycomplete = checkarcerror(xypoints[currentindex:currentindex + arcsegments + 1],
                                                      arc_master.centre, arc_master.radius, arctolerance)

            else:
                arcentitycomplete = True

        if arcentitycomplete:
            arcsegments = arcsegments - 1

        if linesegments >= arcsegments:
            endindex = currentindex + linesegments
            newentitylist.append(Line(xypoints[currentindex], xypoints[endindex]))

            for p in range(endindex - currentindex):
                xydynamiclist.pop(0)

        else:
            # need to recalculate arc here as last arc calculated in loop is outside error bounds and 1 segment too long
            endindex = currentindex + arcsegments
            midpoint = round(arcsegments / 2)

            arc_complete = coordinatestoarc(xypoints[currentindex], xypoints[currentindex + midpoint], xypoints[endindex])

            direction = orientation(xypoints[currentindex], xypoints[currentindex + midpoint], xypoints[endindex])

            if direction == 1:

                #flip start and end points if direction is clockwise
                add_arc = Arc(arc_complete.end, arc_complete.start, arc_complete.centre, arc_complete.radius)
                newentitylist.append(add_arc)

                for p in range(endindex - currentindex):
                    xydynamiclist.pop(0)

            else:
                newentitylist.append(arc_complete)

                for p in range(endindex - currentindex):
                    xydynamiclist.pop(0)

        currentindex = endindex

    #handling end of list where remaining items less than 3 co-ordinates

    if len(xydynamiclist) == 2:
        newentitylist.append(Line(xydynamiclist[0], xydynamiclist[1]))

        for p in range(2):
            xydynamiclist.pop(0)

    elif len(xydynamiclist) == 1:
        xydynamiclist.pop(0)

    return newentitylist

def coordinatesequal(x1y1, x2y2):

    if (x1y1.x == x2y2.x) and (x1y1.y == x2y2.y):
        cordequal = True
    else:
        cordequal = False

    return cordequal

def returnconnectedregions(entitylist):
    newentity = False
    listofregionxy = []
    regionincrement = 0
    dynamicentitylist = entitylist
    regionxy = []
    firstsearchentity = dynamicentitylist[0]
    nextsearchentity = firstsearchentity

    dynamicentitylist.pop(0)

    while len(dynamicentitylist) > 0:

        if newentity:
            regionxy = []
            nextsearchentity = dynamicentitylist[0]
            firstsearchentity = nextsearchentity
            dynamicentitylist.pop(0)
            newentity = False

        connectionfound = False

        for s in range(len(dynamicentitylist)):

            if coordinatesequal(dynamicentitylist[s].start, nextsearchentity.end):
                connectionfound = True
                # add start co-ordinate to output array
                regionxy.append(nextsearchentity.start)

                nextsearchentity = dynamicentitylist[s]
                dynamicentitylist.pop(s)

                if coordinatesequal(firstsearchentity.start, nextsearchentity.end):
                    regionxy.append(nextsearchentity.start)
                    regionxy.append(nextsearchentity.end)

                    # add increment
                    listofregionxy.append(regionxy)
                    regionincrement = regionincrement + 1
                    newentity = True
                break

        if connectionfound == False:
            #not a closed region so throw away points, don't add to list
            newentity = True

    return listofregionxy

def rotate_offset_Coordinate(c, angle, offsetx, offsety):
    anglerads = angle * pi / 180
    xnew = c.x * cos(anglerads) - c.y * sin((anglerads))
    ynew = c.x * sin(anglerads) + c.y * cos((anglerads))
    c_new = Coordinate(xnew+offsetx, ynew+offsety)
    return c_new

def findEntityinRegionfromStartEndCoordinates(c1,c2, searchRegion):

    #searches through a region to find an entity with start and end co-ordinates that match c1,c2
    for entity in searchRegion.entities:
        if c1.x == entity.start.x and c2.x == entity.end.x and c1.y == entity.start.y and c2.y == entity.end.y:
            return entity
        elif c1.x == entity.end.x and c2.x == entity.start.x and c1.y == entity.end.y and c2.y == entity.start.y:
            return entity

    return None
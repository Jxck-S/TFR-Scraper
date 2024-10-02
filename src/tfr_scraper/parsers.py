from coordinates import dms_to_dd
def parse_shape(abd, convert_degrees=True):
        avxs = abd.Avx
        if type(avxs) is list:
            shape = {"type" : "poly", "points" : []}
            #If valBuffer is present it is a linebuffer
            if hasattr(abd, "valBuffer"):
                shape['type'] = "linebuffer"
                shape['valBuffer'] = abd.valBuffer.cdata
            if hasattr(abd, "codeGeoFeatureType"):
                shape['codeGeoFeatureType'] = abd.codeGeoFeatureType.cdata
            if hasattr(abd, "codeBufferBevel"):
                shape['codeBufferBevel'] = abd.codeBufferBevel.cdata
            for point in avxs:
                if hasattr(point, "valRadiusArc") and point.codeType.cdata != "GRC":
                    shape['type'] = "polyarc"
                    shape['arcRadius'] = point.valRadiusArc.cdata
                    pair = (point.geoLatArc.cdata, point.geoLongArc.cdata)
                else:
                    pair = (point.geoLat.cdata, point.geoLong.cdata)
                if convert_degrees:
                    pair = dms_to_dd(pair)
                if shape['type'] == "polyarc" and "arcpoint" not in shape.keys():
                    shape['arcPoint'] = pair
                else:
                    shape["points"].append(pair)

        else:
            if convert_degrees:
                pair = dms_to_dd((avxs.geoLat.cdata, avxs.geoLong.cdata))
            else:
                pair = (avxs.geoLat.cdata, avxs.geoLong.cdata)
            shape = {"type" : "circle", "radius" : avxs.valRadiusArc.cdata, "lat" : pair[0], "lon" : pair[1]}
        return shape

def parse_merged_abd(point_data, convert_degrees=True):
    """
    Converts ABD merged area into a list of coordinates.
    """
    points = []
    for point in point_data:
        pair = (point.geoLat.cdata, point.geoLong.cdata)
        if convert_degrees:
            pair = dms_to_dd(pair)
        points.append(pair)
    return points
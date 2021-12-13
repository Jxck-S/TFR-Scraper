from numpy import compare_chararrays
from untangle import parse


def url_get_contents(url):
        import urllib.request
        req = urllib.request.Request(url=url)
        f = urllib.request.urlopen(req)
        return f.read()
def tfr_list():
    """Downloads TFR table and parses, returns a list of tfrs as dictionaries"""
    url = "https://tfr.faa.gov"
    filepath = "./tfrs.json"
    from html_table_parser.parser import HTMLTableParser
    import pandas as pd
    xhtml = url_get_contents(url).decode('utf-8')
    p = HTMLTableParser()
    p.feed(xhtml)
    df = pd.DataFrame(p.tables[4])
    new_header = df.iloc[2] #grab the first row for the header
    df = df[3:] #take the data less the header row
    df.columns = new_header #set the header row as the df header
    df.replace("", None, inplace=True)
    df = df.dropna(how='any', subset=['NOTAM'])
    print(df)
    tfrs = df.to_dict('records')
    return tfrs
def dms_to_dd(coord_pair):
    """Converts a pair from Degrees Minute Seconds to Decimal Degrees """
    # ("26.02333333N", 097.12833333W") >>  (26.02333333, -97.12833333)
    #FAA coordinates in XML are technically DMS but only NESW part no minutes or seconds, not really a known standard for coordinates 
    directions = {'N':1, 'S':-1, 'E': 1, 'W':-1}
    new_pair = []
    for coord in coord_pair:
        new_pair.append(float(coord.strip("WNSE")) * directions[coord[-1]])
    return new_pair
def parse_tfr(notam_number, convert_degrees=True):
    "Parses a single TFR number for details, downloads details and returns dictionary"
    import requests
    print("Getting details on", notam_number)
    notam_number = notam_number.replace("/", "_")
    url = f"https://tfr.faa.gov/save_pages/detail_{notam_number}.xml"
    try:
        resp = requests.get(url)
        import untangle
        xml = untangle.parse(resp.text)
        XNOTAM = xml.XNOTAM_Update
        paths = ["txtDescrPurpose", 
        "NotUid.txtLocalName" , 
        "dateEffective", 
        "dateExpire",
        "codeTimeZone", 
        "codeExpirationTimeZone",
        ]
        parsed = {}
        for path in paths:
            try:
                if "." in path:
                    key = path.split(".")[-1]
                else:
                    key = path
                parsed[key] = eval(f"XNOTAM.Group.Add.Not.{path}.cdata")
            except:
                pass
        path = "Group.Add.Not.TfrNot.TFRAreaGroup"
        shape_paths = eval(f"XNOTAM.{path}")
        if type(shape_paths) is not list:
            shape_paths = [shape_paths]

        def parse_shape(point_data):
            if type(point_data) is list:
                shape = {"type" : "poly", "points" : []}
                for point in point_data:
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
                    pair = dms_to_dd((point_data.geoLat.cdata, point_data.geoLong.cdata))
                else:
                    pair = (point_data.geoLat.cdata, point_data.geoLong.cdata)
                shape = {"type" : "circle", "radius" : point_data.valRadiusArc.cdata, "lat" : pair[0], "lon" : pair[1]}
            return shape
        def parse_merged_abd(point_data):
            points = []
            for point in point_data:
                pair = (point.geoLat.cdata, point.geoLong.cdata)
                if convert_degrees:
                    pair = dms_to_dd(pair)
                points.append(pair)
            return points
        parsed['shapes'] = []
        known_aseTFRAreaKeys = ["txtName", "valDistVerUpper", "valDistVerLower", "uomDistVerUpper", "uomDistVerLower"]
        for shape_path in shape_paths:
            try:
                if type(shape_path.aseShapes) is not list:
                    shape = parse_shape(shape_path.aseShapes.Abd.Avx)
                else:
                    #Ignores two exact circles
                    not_matching = False
                    compare_to = {}
                    for aseSh in shape_path.aseShapes:
                        try:
                            avx = aseSh.Abd.Avx
                            if compare_to == {}:
                                for key in ["geoLat", "geoLong", "valRadiusArc", "uomRadiusArc"]:
                                    compare_to[key] = eval(f"avx.{key}")
                            else:
                                for key, val in compare_to.items():
                                    if val != eval(f"avx.{key}"):
                                        not_matching = True
                        except AttributeError:
                            not_matching = True
                        if not_matching:
                            break   
                    if not_matching:
                        shape = {"type" : "polyexclude"}
                        shape['all_points'] = parse_merged_abd(shape_path.abdMergedArea.Avx)
                    else:
                        shape = parse_shape(shape_path.aseShapes[0].Abd.Avx)
                if shape['type'] == "polyarc":
                    shape['all_points'] = parse_merged_abd(shape_path.abdMergedArea.Avx)
                for key in known_aseTFRAreaKeys:
                    if hasattr(shape_path.aseTFRArea, key):
                        shape[key] = eval(f"shape_path.aseTFRArea.{key}.cdata")
                parsed['shapes'].append(shape)
            except AttributeError as e:
                print(e)
                if len(shape_path) == 1:
                    parsed['shapes'] = None
        return parsed
    except Exception as e:
        print("Couldn't Parse", notam_number, e)
def get_list_and_parse_all(convert_degrees=True):
    """Downloads list of TFRs and parses all returns basic list combined with details for each (list of dicts)"""
    tfr_list_basic = tfr_list()
    detailed_list = []
    for tfr in tfr_list_basic:
        tfr['details'] = parse_tfr(tfr['NOTAM'], convert_degrees)
        detailed_list.append(tfr)
    return detailed_list 
def save_as_json(input, filepath, indent=None):
    import json
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(input, f, ensure_ascii=False, indent=indent)

def save_detailed_all(filepath="./detailed_tfrs.json"):
    detailed_tfrs = get_list_and_parse_all()
    save_as_json(detailed_tfrs, filepath)
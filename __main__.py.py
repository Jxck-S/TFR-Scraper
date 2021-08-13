def url_get_contents(url):
        import urllib.request
        req = urllib.request.Request(url=url)
        f = urllib.request.urlopen(req)
        return f.read()
def tfr_list():
    url = "https://tfr.faa.gov/tfr2/list.html"
    filepath = "./tfr.json"
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
    df.to_json(filepath, orient='records')
def parse_tfr(notam_number):
    import requests
    import pandas as pd
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
                    shape["points"].append((point.geoLat.cdata, point.geoLong.cdata))

            else:
                shape = {"type" : "circle", "radius" : point_data.valRadiusArc.cdata, "lat" : point_data.geoLat.cdata, "lon" : point_data.geoLong.cdata}
            return shape
        parsed['shapes'] = []
        for shape_path in shape_paths:
            try:
                shape = parse_shape(eval(f"shape_path.aseShapes.Abd.Avx"))
                shape['up_to'] = eval(f"shape_path.aseTFRArea.valDistVerUpper.cdata")
                parsed['shapes'].append(shape)
            except AttributeError:
                if len(shape_path) == 1:
                    parsed['shapes'] = None

        import json
        return parsed
    except Exception as e :
        print("Couldn't Parse", notam_number, e)

def get_list_and_parse():
    tfr_list()
    import json
    f = open('./tfr.json',)
    tfrs = json.load(f)
    detailed = []
    for tfr in tfrs:
        print(tfr["NOTAM"])
        tfr['details'] = parse_tfr(tfr['NOTAM'])
        detailed.append(tfr)
    with open('detailed_tfrs.json', 'w', encoding='utf-8') as f:
        json.dump(detailed, f, ensure_ascii=False, indent=4)
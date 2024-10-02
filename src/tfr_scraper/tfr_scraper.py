from numpy import compare_chararrays
from untangle import parse
from parsers import parse_shape, parse_merged_abd

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

        parsed['shapes'] = []
        known_aseTFRAreaKeys = ["txtName", "valDistVerUpper", "valDistVerLower", "uomDistVerUpper", "uomDistVerLower", "codeExclVerUpper", "codeExclVerLower", "isScheduledTfrArea"]
        for shape_path in shape_paths:
            try:
                if type(shape_path.aseShapes) is not list:
                    shape = parse_shape(shape_path.aseShapes.Abd)
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
                        shape = parse_shape(shape_path.aseShapes[0].Abd)

                #If Polyarc or linebuffer parse full outline, all coordinates (abdMergedArea)
                if shape['type'] in ["polyarc", "linebuffer"]:
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
def save_detailed_all_cleaned(filepath="./detailed_tfrs.json"):
    detailed_tfrs = get_list_and_parse_all()
    cleaned_tfrs = []
    for tfr in detailed_tfrs:
        #Fix for Washington DC TFR 
        if tfr['NOTAM'] == '1/1155':
            tfr['details']['shapes'][0]['valDistVerUpper'] = 18000
        cleaned_tfrs.append(tfr)
    save_as_json(cleaned_tfrs, filepath)

def detailed_all_cleaned():
    detailed_tfrs = get_list_and_parse_all()
    cleaned_tfrs = []
    for tfr in detailed_tfrs:
        #Fix for Washington DC TFR
        if tfr['NOTAM'] == '1/1155':
            tfr['details']['shapes'][0]['valDistVerUpper'] = 18000
        cleaned_tfrs.append(tfr)
    return cleaned_tfrs
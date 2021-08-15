# TFR-Scraper
Scrapes TFRs from FAA site https://tfr.faa.gov/ and able to parse details per xml of TFR. 

## Requirements
- html_table_parser.parser https://pypi.org/project/html-table-parser-python3/
- untangle https://pypi.org/project/untangle/
- pandas https://pypi.org/project/pandas/

### TFR/Shape types
- TFRs have many types weather it be just a circle or a polygon or a TFR can have multiple circles/polygons, this scraper will parse each. 
- Below is an example of each and the type of shapes the parser will return for each 
#### Single Circle 
![Alt text](examples/type-images/Single-Circle.gif?raw=true "Single Circle"){:height="50%" width="50%"}
```json
            "shapes": [
                {
                    "type": "circle",
                    "radius": "5.0",
                    "lat": "40.74388889N",
                    "lon": "111.65527778W",
                    "up_to": "12500"
                }
```
#### Single Polygon
 ![Alt text](examples/type-images/Single-Poly.gif?raw=true "Single Poly"){:height="50%" width="50%"}
```json
            "shapes": [
                {
                    "type": "poly",
                    "points": [
                        [
                            "46.59583333N",
                            "116.54111111W"
                        ],
                        [
                            "46.61666667N",
                            "116.47388889W"
                        ],
                        [
                            "46.55833333N",
                            "116.40638889W"
                        ],
                        [
                            "46.5125N",
                            "116.42416667W"
                        ],
                        [
                            "46.50055556N",
                            "116.53722222W"
                        ],
                        [
                            "46.51416667N",
                            "116.62916667W"
                        ]
                    ],
                    "up_to": "8500"
```
#### Multi Circle
![Alt text](examples/type-images/Multi-Circle.gif?raw=true "Multi Circle"){:height="50%" width="50%"}
```json
            "shapes": [
                {
                    "type": "circle",
                    "radius": "10.0",
                    "lat": "39.64805556N",
                    "lon": "077.46666667W",
                    "up_to": "17999"
                },
                {
                    "type": "circle",
                    "radius": "5.0",
                    "lat": "39.64805556N",
                    "lon": "077.46666667W",
                    "up_to": "17999"
                }
            ]
```
## TFR Json objects
Single tfr object from list w/o details parsed
```json [
    {
        "Date": "08/13/2021",
        "NOTAM": "1/7932",
        "Facility": "ZSE",
        "State": "CA",
        "Type": "HAZARDS",
        "Description": "35NM SE YREKA, CA, Friday, August 13, 2021 through Sunday, September 05, 2021 UTC New",
        "Zoom": ""
    },
```
A detailed object when combined with info from list
```json 
    {
        "Date": "08/13/2021",
        "NOTAM": "1/7932",
        "Facility": "ZSE",
        "State": "CA",
        "Type": "HAZARDS",
        "Description": "35NM SE YREKA, CA, Friday, August 13, 2021 through Sunday, September 05, 2021 UTC New",
        "Zoom": "",
        "details": {
            "txtDescrPurpose": "TO PROVIDE A SAFE ENVIRONMENT FOR FIRE FIGHTING AVIATION OPS",
            "txtLocalName": "1/7932",
            "dateEffective": "2021-08-13T18:15:00",
            "dateExpire": "2021-09-05T05:00:00",
            "codeTimeZone": "UTC",
            "codeExpirationTimeZone": "UTC",
            "shapes": [
                {
                    "type": "poly",
                    "points": [
                        [
                            "41.4N",
                            "122.13333333W"
                        ],
                        [
                            "41.72083333N",
                            "121.94166667W"
                        ],
                        [
                            "41.625N",
                            "121.7W"
                        ],
                        [
                            "41.43333333N",
                            "121.78333333W"
                        ],
                        [
                            "41.4N",
                            "122.13333333W"
                        ]
                    ],
                    "up_to": "10500"
                }
            ]
        }
    }
```

# TFR-Scraper
Scrapes TFRs from FAA site https://tfr.faa.gov/ and able to parse details per xml of TFR. 

## Requirements
- html_table_parser.parser https://pypi.org/project/html-table-parser-python3/
- untangle https://pypi.org/project/untangle/
- pandas https://pypi.org/project/pandas/

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

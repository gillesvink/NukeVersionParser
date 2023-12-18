[![python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![Last parse run](https://github.com/gillesvink/NukeVersionParser/actions/workflows/test_and_deploy.yaml/badge.svg)

# NukeVersionParser
An automatic parser that generates JSON reports containing the latest Nuke versions. For an up-to-date graphical view of what is still supported by Foundry, visit [Foundry's support page](https://support.foundry.com/hc/en-us/articles/360019296599).

Example from the provided JSON files (nuke-minor-supported-releases.json):
```json
{
    "15": {
        "15.0v2": {
            "installer": {
                "mac_arm": "https://thefoundry.s3.amazonaws.com/products/nuke/releases/15.0v2/Nuke15.0v2-mac-arm64.dmg",
                "mac_x86": "https://thefoundry.s3.amazonaws.com/products/nuke/releases/15.0v2/Nuke15.0v2-mac-x86_64.dmg",
                "linux_x86": "https://thefoundry.s3.amazonaws.com/products/nuke/releases/15.0v2/Nuke15.0v2-linux-x86_64.tgz",
                "windows_x86": "https://thefoundry.s3.amazonaws.com/products/nuke/releases/15.0v2/Nuke15.0v2-win-x86_64.zip"
            },
            "date": "Wed, 15 Nov 2023 15:08:31 GMT",
            "supported": true
        }
    },
}
```


## Why?
This tool is designed for the automatic building of plugins. 
It eliminates the need to manually specify versions, 
making scripts relying on the JSON able to automate their building process.

## What data does it collect?
* Nuke families with all their versions, 
  following semantic versioning 
  (Major = Family, Minor = Feature improvements, Patch = Bugfixes).
* Release dates for each Nuke version.
* A boolean indicating whether a Nuke version is still supported 
  (versions older than 18 months are considered unsupported).
* URLs for all possible executables 
  (Linux X86, Windows X86, Mac X86, and Mac ARM).

There are 4 exported JSON files:

* `nuke-all-releases.json`: this contains all data available, unfiltered.
* `nuke-all-supported-releases.json`: this contains all data 
   to releases that are still supported by Foundry.
* `nuke-minor-releases.json`: this contains all minor releases.
* `nuke-minor-supported-releases.json`: this contains all minor
   releases that are currently still supported.

## How does it work?
The tool scans the server for all executables, 
constructing the JSON from the collected data. 

The repository is updated only if there is new information. 
There is no manual process, ensuring it stays up-to-date automatically. 
(It can take 24 hours for new executables to show up in the JSON). 

This means the naming scheme should stay the same. If this changes, this can be adapted in the `url_calculator.py`.

## How to use?
Retrieve the raw JSON links for use in your scripts. 
As JSON is not restricted to any language, it can be used anywhere. 
Multiple JSON files serve different purposes. 

For example, when compiling plugins, you might only need the JSON 
showing the latest minor versions (nuke-minor-releases.json), avoiding unnecessary compilations.

This can for example be used in Python to retrieve data easily. 
For example a dialog could be implemented to show if an update is available, 
and download that newer version. (See example)

### Example
To collect the data in Python as a dictionary, you can run this code:
```python
import requests

requested_data = requests.get(
    "https://raw.githubusercontent.com/gillesvink/NukeVersionParser/main/nuke-minor-releases.json"
)
supported_releases = requested_data.json()
nuke_15_data = supported_releases.get("15")

print(nuke_15_data)
>> {'15.0v2': {'installer': {'mac_arm': 'https://thefoundry.s3.amazonaws.com/products/nuke/releases/15.0v2/Nuke15.0v2-mac-arm64.dmg', 'mac_x86': 'https://thefoundry.s3.amazonaws.com/products/nuke/releases/15.0v2/Nuke15.0v2-mac-x86_64.dmg', 'linux_x86': 'https://thefoundry.s3.amazonaws.com/products/nuke/releases/15.0v2/Nuke15.0v2-linux-x86_64.tgz', 'windows_x86': 'https://thefoundry.s3.amazonaws.com/products/nuke/releases/15.0v2/Nuke15.0v2-win-x86_64.zip'}, 'date': 'Wed, 15 Nov 2023 15:08:31 GMT', 'supported': True}}
```

## Requests/Issues
If you feel like something could be added or if something is 
not working as it should, feel free to make an issue on this repository.

## Disclaimer
This project is an independent effort, not affiliated with or endorsed by Foundry. 
It retrieves data from all Nuke versions for automatic building purposes. 
The terms "Nuke" and related trademarks are the property of Foundry, 
used here for descriptive purposes only. For official information and support, 
please refer to Foundry's [official website](https://www.foundry.com/).

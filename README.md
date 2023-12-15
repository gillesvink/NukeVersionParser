# NukeVersionParser
An automatic parser that generates JSON reports containing the latest Nuke versions. For an up-to-date graphical view of what is still supported by Foundry, visit [Foundry's support page](https://support.foundry.com/hc/en-us/articles/360019296599).

## Why?
This tool is designed for the automatic building of plugins. It eliminates the need to manually specify versions, making scripts relying on the JSON able to automate their building process.

## What Data Does It Collect?
* Nuke families with all their versions, following semantic versioning (Major = Family, Minor = Feature improvements, Patch = Bugfixes).
* Release dates for each Nuke version.
* A boolean indicating whether a Nuke version is still supported (versions older than 18 months are considered unsupported).
* URLs for all possible executables (Linux X86, Windows X86, Mac X86, and Mac ARM).

There are 4 exported JSON files:

* `nuke-all-releases.json`: this contains all data available, unfiltered.
* `nuke-all-supported-releases.json`: this contains all data to releases that are still supported by Foundry.
* `nuke-minor-releases.json`: this contains all minor releases.
* `nuke-minor-supported-releases.json`: this contains all minor releases that are currently still supported.

## How Does It Work?
The tool scans the server for all executables, constructing the JSON from the collected data. The repository is updated only if there is new information. There is no manual process, ensuring it stays up-to-date automatically. (It can take 24 hours for new executables to show up in the JSON). 

This means the naming scheme should stay the same. If this changes, this can be adapted in the `url_calculator.py`.

## How to Use?
Retrieve the raw JSON links for use in your scripts. As JSON is not restricted to any language, it can be used anywhere. Multiple JSON files serve different purposes. For example, when compiling plugins, you may only need the JSON showing the latest minor versions (nuke-minor-releases.json), avoiding unnecessary recompilations.

This can for example be used in Python to retrieve data easily. For example a dialog could be implemented to show if an update is available, and download that newer version.

### Example
To collect the data in Python as a dictionary, you can run this code:
```python
import requests

requested_data = requests.get("https://github.com/gillesvink/NukeVersionParser/nuke-minor-supported-releases.json")
minor_supported_releases_json = minor_supported_release.json()

nuke_15_data = minor_supported_releases_json.get("15")
```

## Disclaimer
This project is an independent effort, not affiliated with or endorsed by Foundry. It retrieves data from all Nuke versions for automatic building purposes. The terms "Nuke" and related trademarks are the property of Foundry, used here for descriptive purposes only. For official information and support, please refer to Foundry's [official website](https://www.foundry.com/).

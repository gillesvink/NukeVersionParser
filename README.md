# AllNukeVersions
Automatic parser that reports in a JSON all latest Nuke versions.
For an up-to-date view of what is still supported by Foundry visit: https://support.foundry.com/hc/en-us/articles/360019296599.

## Why?
This is useful for automatic building of plugins, using all the existing Nuke versions. This eliminates the need to specify all versions manually if the script is relying on the JSON.

## How does it work?
It scans the server for all executables. Out of that data, it builds the JSON. Only if there is anything new, the repo will be updated.
There is no manual process done here, making sure it will stay up-to-date until the executable naming externally has changed.

## How to use?
The raw link to the JSON's can be used to retrieve date in your own scripts. There are multiple JSON files, each with their own purpose.
For example it might only be needed when compiling plugins to look at the JSON that shows the latest minor versions, not the different small versions, as then the plugin does not need to be recompiled.

## What data does it collect?
* Nuke Family's with all their versions. This follows their semantic versioning. So Major = Family, Minor = Feature improvements, Patch = bugfixes.
* For each Nuke version the date when they've released
* Bool reporting if Nuke version is still supported (basically anything older then 18 months is not supported anymore)
* All url's for possible executables (Linux, Windows, Mac X86 and ARM)
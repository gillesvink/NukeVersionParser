# AllNukeVersions
Automatic parser that reports in a JSON all latest Nuke versions. It depends on the table data set on https://support.foundry.com/hc/en-us/articles/360019296599.

## Why?
This is useful for automatic building of plugins, using all the existing Nuke versions. This eliminates the need to specify all versions manually.

## How does it work?
It scans the page once a day and checks if there is anything new. If that is the case, it will be added to the JSON that is placed in this repo.
There is no manual process done here, making sure it will stay up-to-date until this page has been modified.


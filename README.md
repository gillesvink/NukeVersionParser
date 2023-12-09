# AllNukeVersions
An automatic parser that generates a JSON report containing the latest Nuke versions. For an up-to-date view of what is still supported by Foundry, visit [Foundry's support page](https://support.foundry.com/hc/en-us/articles/360019296599).

## Why?
This tool is designed for the automatic building of plugins, leveraging all existing Nuke versions. It eliminates the need to manually specify versions, making scripts relying on the JSON able to automate their building process.

## What Data Does It Collect?
* Nuke families with all their versions, following semantic versioning (Major = Family, Minor = Feature improvements, Patch = Bugfixes).
* Release dates for each Nuke version.
* A boolean indicating whether a Nuke version is still supported (versions older than 18 months are considered unsupported).
* URLs for possible executables (Linux, Windows, Mac X86, and ARM).

## How Does It Work?
The tool scans the server for all executables, constructing the JSON from the collected data. The repository is updated only if there is new information. There is no manual process, ensuring it stays up-to-date automatically. (It can take 24 hours for new executables to show up in the JSON)

## How to Use?
Retrieve the raw JSON links for use in your scripts. Multiple JSON files serve different purposes. For example, when compiling plugins, you may only need the JSON showing the latest minor versions, avoiding unnecessary recompilations.

## Disclaimer
This project is an independent effort, not affiliated with or endorsed by Foundry. It retrieves data from all Nuke versions for automatic building purposes. The terms "Nuke" and related trademarks are the property of Foundry, used here for descriptive purposes only. For official information and support, please refer to Foundry's [official website](https://www.foundry.com/).

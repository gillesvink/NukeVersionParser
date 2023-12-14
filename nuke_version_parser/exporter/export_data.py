"""Script that is responsible for preparing and exporting data.

@maintainer: Gilles Vink
"""

from __future__ import annotations

import copy
import json
import logging
from collections import defaultdict
from dataclasses import astuple
from operator import attrgetter
from pathlib import Path

from nuke_version_parser.datamodel.nuke_data import NukeFamily
from nuke_version_parser.parser.collector import collect_families

logger = logging.getLogger(__name__)

__slots__ = ("collect_and_write_json_files",)


def _sort_families(families: list[NukeFamily]) -> None:
    """Sort provided data into ascending order.

    This means major -> minor - > patch.

    Args:
        families: data to sort.
    """
    families.sort(key=attrgetter("version"), reverse=True)
    for family in families:
        family.releases.sort(key=astuple, reverse=True)


def _convert_to_only_minor_releases(families: list[NukeFamily]) -> None:
    """Reduce families to only contain minor releases

    Note: this function respects the original order of the list.

    Args:
        families: list of families to reduce into only minor releases.
    """
    for family in families:
        minor_versions = defaultdict(list)

        for release in family.releases:
            minor_versions[release.version.minor].append(release)

        collected_releases = [
            max(minor_releases, key=attrgetter("version.patch"))
            for minor_releases in minor_versions.values()
        ]

        family.releases = collected_releases


def _convert_data_to_json(families: list[NukeFamily]) -> str:
    """Convert provided families to a JSON.

    Args:
        families: list of NukeFamily objects to convert to JSON.

    Returns:
        the converted JSON string.
    """
    collected_data = {}
    for family in families:
        collected_data.update(family.to_dict())
    return json.dumps(collected_data, indent=4)


def _write_json_to_file(json_data: str, file_path: Path) -> None:
    """Write provided JSON to provided file path.

    Args:
        json_data: data to write in file.
        file_path: path where to store the json file.
    """
    if file_path.suffix != ".json":
        msg = "Provided path does not end with .json"
        raise ValueError(msg)
    file_path.write_text(json_data)


def _reduce_to_only_supported(families: list[NukeFamily]) -> None:
    """Reduce provided families to only return supported."""
    supported_families = [
        family for family in families if family.get_supported()
    ]
    for family in supported_families:
        family.releases = [
            release for release in family.releases if release.get_supported()
        ]
    families[:] = supported_families


def collect_and_write_json_files(directory: Path) -> None:
    """Call the collector and write these files to specified path.

    This will write out two files. One for all releases, the
    second for only the latest minor releases.

    Args:
        directory: path to write files to.
    """
    all_data = collect_families()
    logging.info("Done collecting all families data.")

    _sort_families(all_data)

    only_minor_releases = copy.deepcopy(all_data)
    all_supported_data = copy.deepcopy(all_data)
    _convert_to_only_minor_releases(only_minor_releases)

    _reduce_to_only_supported(all_supported_data)
    only_minor_supported_releases = copy.deepcopy(all_supported_data)
    _convert_to_only_minor_releases(only_minor_supported_releases)

    only_minor_json = _convert_data_to_json(only_minor_releases)
    only_minor_supported_json = _convert_data_to_json(
        only_minor_supported_releases
    )
    all_releases_json = _convert_data_to_json(all_data)
    all_supported_releases_json = _convert_data_to_json(all_supported_data)
    logging.info("Converted all data to JSON.")

    only_minor_path = directory / "nuke-minor-releases.json"
    only_minor_supported_path = (
        directory / "nuke-minor-supported-releases.json"
    )
    all_releases_path = directory / "nuke-all-releases.json"
    all_supported_releases_path = (
        directory / "nuke-all-supported-releases.json"
    )

    _write_json_to_file(
        json_data=only_minor_json,
        file_path=only_minor_path,
    )
    _write_json_to_file(
        json_data=all_releases_json,
        file_path=all_releases_path,
    )
    _write_json_to_file(
        json_data=only_minor_supported_json,
        file_path=only_minor_supported_path,
    )
    _write_json_to_file(
        json_data=all_supported_releases_json,
        file_path=all_supported_releases_path,
    )

    logging.info("Done writing JSON files.")

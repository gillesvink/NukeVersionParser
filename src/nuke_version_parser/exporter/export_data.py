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
from typing import TYPE_CHECKING

from nuke_version_parser.parser.collector import collect_families

if TYPE_CHECKING:
    from pathlib import Path

    from nuke_version_parser.datamodel.nuke_data import NukeFamily

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


def _reduce_to_only_minor_releases(families: list[NukeFamily]) -> None:
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


def _create_all_json(families: list[NukeFamily]) -> str:
    """Create all releases JSON.

    Args:
        families: family data to convert to supported releases

    Returns:
        str: collected data as JSON.
    """
    data = copy.deepcopy(families)
    return _convert_data_to_json(data)


def _create_all_supported_json(families: list[NukeFamily]) -> str:
    """Create all supported JSON.

    Args:
        families: family data to convert to minor supported releases

    Returns:
        str: collected data as JSON.
    """
    data = copy.deepcopy(families)
    _reduce_to_only_supported(data)
    return _convert_data_to_json(data)


def _create_minor_json(families: list[NukeFamily]) -> str:
    """Create minor releases JSON.

    Args:
        families: family data to convert to supported releases

    Returns:
        str: collected data as JSON.
    """
    data = copy.deepcopy(families)
    _reduce_to_only_minor_releases(data)
    return _convert_data_to_json(data)


def _create_minor_supported_json(families: list[NukeFamily]) -> str:
    """Create minor supported JSON.

    Args:
        families: family data to convert to minor supported releases

    Returns:
        str: collected data as JSON.
    """
    data = copy.deepcopy(families)
    _reduce_to_only_minor_releases(data)
    _reduce_to_only_supported(data)
    return _convert_data_to_json(data)


def collect_and_write_json_files(directory: Path) -> None:
    """Call the collector and write these files to specified path.

    This will write out two files. One for all releases, the
    second for only the latest minor releases.

    Args:
        directory: path to write files to.
    """
    try:
        all_data = collect_families()
        logging.info("Done collecting all families data.")
    except TimeoutError:
        msg = "No active internet connection, could not fetch data."
        logging.warning(msg)
        return

    _sort_families(all_data)

    _write_json_to_file(
        json_data=_create_minor_json(all_data),
        file_path=directory / "nuke-minor-releases.json",
    )
    _write_json_to_file(
        json_data=_create_all_json(all_data),
        file_path=directory / "nuke-all-releases.json",
    )
    _write_json_to_file(
        json_data=_create_minor_supported_json(all_data),
        file_path=directory / "nuke-minor-supported-releases.json",
    )
    _write_json_to_file(
        json_data=_create_all_supported_json(all_data),
        file_path=directory / "nuke-all-supported-releases.json",
    )

    logging.info("Done writing JSON files.")

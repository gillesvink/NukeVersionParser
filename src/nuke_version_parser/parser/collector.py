"""File that contains the FamilyCollector object.

This object is responsible for fetching family data.

@maintainer: Gilles Vink
"""

from __future__ import annotations

from copy import deepcopy

from nuke_version_parser.datamodel.nuke_data import (
    NukeFamily,
    NukeRelease,
    SemanticVersion,
)
from nuke_version_parser.parser.parse_data import (
    parse_release_data_by_attribute,
)

__slots__ = ("collect_families",)


def _get_all_families() -> list[NukeFamily]:
    """Return a list of NukeFamilies.

    Note:
        this is only major versions.
    """
    releases = parse_release_data_by_attribute(
        SemanticVersion(9, 0, 1), "major"
    )
    return [NukeFamily([release]) for release in releases]


def _find_all_minor_versions(
    family: NukeFamily,
) -> None:
    """Find all minor versions and add them to the family.

    Args:
        family: to find minor versions from.
    """
    found_release: NukeRelease = family.releases[0]
    version = deepcopy(found_release.version)
    version.minor += 1
    minor_versions = parse_release_data_by_attribute(version, "minor")
    family.releases.extend(minor_versions)


def _find_all_patch_versions(
    family: NukeFamily,
) -> list[NukeRelease]:
    """Find all minor versions and add them to the family.

    Args:
        family: to find minor versions from.
    """
    patch_versions = []
    for release in family.releases:
        version = deepcopy(release.version)
        version.patch += 1
        patch_versions.extend(
            parse_release_data_by_attribute(version, "patch")
        )
    family.releases.extend(patch_versions)


def collect_families() -> list[NukeFamily]:
    """Fetch and collect all releases into families."""
    families = _get_all_families()
    for family in families:
        _find_all_minor_versions(family)
        _find_all_patch_versions(family)
    return families

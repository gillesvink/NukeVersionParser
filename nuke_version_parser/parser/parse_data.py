"""Script that scans for all possible data.

@maintainer: Gilles Vink
"""
from __future__ import annotations

import logging
from copy import deepcopy

import requests

from nuke_version_parser.datamodel.constants import (
    Architecture,
    OperatingSystem,
)
from nuke_version_parser.datamodel.nuke_data import (
    NukeFamily,
    NukeInstaller,
    NukeRelease,
    SemanticVersion,
)
from nuke_version_parser.parser.url_calculator import calculate_url

__slots__ = ("FamilyCollector",)

logger = logging.getLogger(__name__)


class _VersionParser:
    """Object that is responsible for fetching data by version."""

    def __init__(self, version: SemanticVersion) -> None:
        self._version = version
        self._date: str | None = None

    @classmethod
    def to_nuke_release(cls, version: SemanticVersion) -> NukeRelease | None:
        """Parse data from version to NukeRelease.

        Args:
            version: version to parse data for.

        Returns:
            NukeRelease if data found else None
        """
        version_parser = cls(version)
        linux_x86 = version_parser.retrieve_data(
            system=OperatingSystem.LINUX, architecture=Architecture.X86
        )
        windows_x86 = version_parser.retrieve_data(
            system=OperatingSystem.WINDOWS, architecture=Architecture.X86
        )
        mac_x86 = version_parser.retrieve_data(
            system=OperatingSystem.MAC, architecture=Architecture.X86
        )
        mac_arm = version_parser.retrieve_data(
            system=OperatingSystem.LINUX, architecture=Architecture.ARM
        )

        if not version_parser.date:
            return None

        installer_data = NukeInstaller(
            linux_x86=linux_x86,
            windows_x86=windows_x86,
            mac_x86=mac_x86,
            mac_arm=mac_arm,
        )
        return NukeRelease(
            version=version, installer=installer_data, date=version_parser.date
        )

    def retrieve_data(
        self, system: OperatingSystem, architecture: Architecture
    ) -> str | None:
        """Retrieve data from Nuke release using provided arguments.

        Args:
            operating_system: operating system to find executable for
            architecture: architecture to find release for

        Returns:
            url of release if found, None if not found.
        """
        calculated_url = calculate_url(
            version=self._version, system=system, architecture=architecture
        )
        response = requests.head(calculated_url, timeout=1)
        if response.status_code != 200:
            msg = f"Found no data for {calculated_url}"
            logger.info(msg)
            return None

        if not self._date:
            self._date = response.headers.get("last-modified")

        msg = f"Processed {calculated_url}"
        logger.info(msg)

        return calculated_url

    @property
    def date(self) -> str | None:
        """Return the cached date.

        Returns:
            str of date if found, else None.
        """
        return self._date


def _parse_release_data_by_attribute(
    start_version: SemanticVersion, attribute_name: str
) -> list[NukeRelease]:
    """Parse data by start version and iterate over provided attribute.

    Args:
        start_version: version to start iteration with
        attribute_name: attribute name to use for iterating

    Returns:
        list of NukeRelease if found, else empty list.
    """
    latest_version = deepcopy(start_version)
    previous_release = _VersionParser.to_nuke_release(start_version)
    if not previous_release:
        return []

    nuke_releases = [previous_release]

    while previous_release:
        latest_version = deepcopy(latest_version)
        attribute_value = getattr(latest_version, attribute_name)
        setattr(latest_version, attribute_name, attribute_value + 1)
        release = _VersionParser.to_nuke_release(latest_version)
        if release:
            nuke_releases.append(release)
        previous_release = release

    return nuke_releases


class FamilyCollector:
    """Object that handles the collection of family data."""

    START_VERSION = SemanticVersion(9, 0, 1)
    """First version that will be looked for."""

    def __new__(cls) -> None:
        """Fetch and collect all releases into families."""
        families = cls._get_all_families()
        for family in families:
            cls._find_all_minor_versions(family)
            cls._find_all_patch_versions(family)
        return families

    @classmethod
    def _get_all_families(cls) -> list[NukeFamily]:
        """Return a list of NukeFamilies.

        Note:
            this is only major versions.
        """
        releases = _parse_release_data_by_attribute(
            cls.START_VERSION, "major"
        )
        return [NukeFamily([release]) for release in releases]

    @staticmethod
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
        minor_versions = _parse_release_data_by_attribute(version, "minor")
        family.releases.extend(minor_versions)

    @staticmethod
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
                _parse_release_data_by_attribute(version, "patch")
            )
        family.releases.extend(patch_versions)

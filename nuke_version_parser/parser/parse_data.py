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
    NukeInstaller,
    NukeRelease,
    SemanticVersion,
)
from nuke_version_parser.parser.url_calculator import calculate_url

__slots__ = ("parse_release_data_by_attribute",)

logger = logging.getLogger(__name__)


class _VersionParser:
    """Object that is responsible for fetching data by version."""

    def __init__(self, version: SemanticVersion) -> None:
        """Create instance of the VersionParser object.

        Args:
            version: version to use for collecting data.
        """
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
        linux_x86_64 = version_parser.retrieve_data(
            system=OperatingSystem.LINUX, architecture=Architecture.X86_64
        )
        windows_x86_64 = version_parser.retrieve_data(
            system=OperatingSystem.WINDOWS, architecture=Architecture.X86_64
        )
        mac_x86_64 = version_parser.retrieve_data(
            system=OperatingSystem.MAC, architecture=Architecture.X86_64
        )
        mac_arm = version_parser.retrieve_data(
            system=OperatingSystem.MAC, architecture=Architecture.ARM
        )

        if not version_parser.date:
            return None

        installer_data = NukeInstaller(
            linux_x86_64=linux_x86_64,
            windows_x86_64=windows_x86_64,
            mac_x86_64=mac_x86_64,
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
        response = requests.head(calculated_url, timeout=10)
        if response.status_code != 200:  # noqa: PLR2004
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


def parse_release_data_by_attribute(
    start_version: SemanticVersion, attribute_name: str
) -> list[NukeRelease]:
    """Parse data by start version and iterate over provided attribute.

    Args:
        start_version: version to start iteration with
        attribute_name: attribute name to use for iterating

    Returns:
        list of NukeRelease if found, else empty list.
    """
    latest_version = _get_version_to_process(start_version)
    previous_release = _VersionParser.to_nuke_release(latest_version)
    if not previous_release:
        return []

    nuke_releases = [previous_release]

    while previous_release:
        latest_version = _get_version_to_process(latest_version)
        attribute_value = getattr(latest_version, attribute_name)
        setattr(latest_version, attribute_name, attribute_value + 1)
        release = _VersionParser.to_nuke_release(latest_version)
        if release:
            nuke_releases.append(release)
        previous_release = release

    return nuke_releases


def _get_version_to_process(
    version: SemanticVersion,
) -> SemanticVersion:
    """Check and return the version to be jumped to.

    Args:
        version: current version

    Returns:
        Either None or the version to jump to.
    """
    version_10_5 = SemanticVersion(10, 5, 1)
    if version > SemanticVersion(10, 0, 6) and version < version_10_5:
        return version_10_5
    return deepcopy(version)

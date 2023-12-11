"""Script that scans for all possible data.

@maintainer: Gilles Vink
"""
from __future__ import annotations
from copy import deepcopy
import requests
from nuke_version_parser.datamodel.nuke_data import (
    NukeInstaller,
    NukeRelease,
    SemanticVersion,
)
from nuke_version_parser.parser.url_calculator import calculate_url
from nuke_version_parser.datamodel.constants import (
    OperatingSystem,
    Architecture,
)


class VersionParser:
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
        response = requests.get(calculated_url, timeout=1)
        if response.status_code != 200:
            return None

        if not self._date:
            self._date = response.headers.get("last-modified")
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
) -> set[NukeRelease]:
    """Parse data by start version and iterate over provided attribute.

    Args:
        start_version: version to start iteration with
        attribute_name: attribute name to use for iterating

    Returns:
        set of NukeRelease if found, else empty set.
    """
    latest_version = deepcopy(start_version)
    previous_release = VersionParser.to_nuke_release(start_version)
    if not previous_release:
        return set()

    nuke_releases = {previous_release}

    while previous_release:
        latest_version = deepcopy(latest_version)
        attribute = getattr(latest_version, attribute_name)
        setattr(latest_version, attribute_name, attribute + 1)
        release = VersionParser.to_nuke_release(latest_version)
        if release:
            nuke_releases.add(release)
        previous_release = release

    return nuke_releases

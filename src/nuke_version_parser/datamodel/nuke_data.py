"""Datamodel that is able to store all data related to Nuke versions.

@maintainer: Gilles Vink
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass
class SemanticVersion:
    """Data object to store a semantic version."""

    major: int
    """The big release of software."""
    minor: int
    """The feature improvement release."""
    patch: int
    """Bugfix release."""

    def __str__(self) -> str:
        """Return object in string format."""
        return f"{self.major}.{self.minor}v{self.patch}"

    def __gt__(self, other: SemanticVersion) -> bool:
        """Greater than implementation.

        Args:
            other: other object to compare to.

        Raises:
            TypeError: if provided object is not a SemanticVersion.

        Returns:
            True if greater than, False if not.
        """
        if not isinstance(other, self.__class__):
            msg = "Comparison only allowed to SemanticVersion object."
            raise TypeError(msg)
        if self == other:
            return False
        if self.major != other.major:
            return self.major > other.major
        if self.minor != other.minor:
            return self.minor > other.minor
        return self.patch > other.patch

    def __lt__(self, other: SemanticVersion) -> bool:
        """Lower than implementation.

        Args:
            other: other object to compare to.

        Returns:
            True if smaller than, False if not.
        """
        if self == other:
            return False
        return not self.__gt__(other)


@dataclass
class NukeInstaller:
    """Data related to the installer a Nuke release."""

    mac_arm: str = None
    """URL to the Mac ARM (M1, M2..) installer.
    Note: only supported from Nuke 15+"""
    mac_x86_64: str = None
    """URL to the Mac installer."""
    linux_x86_64: str = None
    """URL to the Linux installer."""
    windows_x86_64: str = None
    """URL to the Windows installer."""


@dataclass
class NukeRelease:
    """Data related to a specific release of Nuke."""

    version: SemanticVersion
    """Semantic version data of the release."""
    installer: NukeInstaller
    """Installer data."""
    date: str
    """Date of release."""

    def get_supported(self) -> bool:
        """Return True if supported, False if not.

        This returns False if the release date is older than 18 months.
        """
        if not self.date:
            msg = "No date is set, can't get supported state."
            raise ValueError(msg)

        collected_date = datetime.strptime(
            self.date, "%a, %d %b %Y %H:%M:%S %Z"
        ).replace(tzinfo=timezone.utc)
        current_date = datetime.now(timezone.utc)

        days_between: int = (current_date - collected_date).days
        if days_between <= 548:  # this is roughly 18 months  # noqa: PLR2004
            return True
        return False

    def to_dict(self) -> dict[str, dict[str, Any]]:
        """Return a dict with all data."""
        return {
            str(self.version): {
                "installer": asdict(self.installer),
                "date": self.date,
                "supported": self.get_supported(),
            }
        }


@dataclass
class NukeFamily:
    """Data containing everything related to a family of Nuke versions."""

    releases: list[NukeRelease]
    """List of releases part of this family."""

    def __post_init__(self) -> None:
        """Check if provided NukeVersions are compatible.

        Raises:
            IncompatibleFamilyError: if versions are not the same major.
        """
        all_versions = {release.version.major for release in self.releases}
        if len(all_versions) != 1:
            msg = (
                f"Family contains more than one major version: {all_versions}."
            )
            raise IncompatibleFamilyError(msg)

    @property
    def version(self) -> int:
        """Return the version identifier of this family."""
        semantic_version: SemanticVersion = self.releases[0].version
        return semantic_version.major

    def get_supported(self) -> bool:
        """Return bool containing supported status."""
        return any(version.get_supported() for version in self.releases)

    def to_dict(self) -> dict:
        """Convert the NukeFamily to a dictionary containing all releases."""
        combined_data = {}
        for release in self.releases:
            release_dict = release.to_dict()
            combined_data.update(release_dict)

        return {self.version: combined_data}


class IncompatibleFamilyError(Exception):
    """Exception that is raised when a Nuke Family is incompatible."""

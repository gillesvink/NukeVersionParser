"""Datamodel that is able to store all data related to Nuke versions.

@maintainer: Gilles Vink
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SemanticVersion:
    """Data object to store a semantic version."""

    major: int
    """The big release of software."""
    minor: int
    """The feature improvement release."""
    patch: int
    """Bugfix release."""


@dataclass
class NukeInstaller:
    """Data related to the installer a Nuke release."""

    mac_x86: str
    """URL to the Mac installer."""
    linux_x86: str
    """URL to the Linux installer."""
    windows_x86: str
    """URL to the Windows installer."""
    mac_arm: str = None
    """URL to the Mac ARM (M1, M2..) installer.
    Note: only supported from Nuke 15+"""


@dataclass
class NukeRelease:
    """Data related to a specific release of Nuke."""

    version: SemanticVersion
    """Semantic version data of the release."""
    installer: NukeInstaller
    """Installer data."""


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
        all_versions = {
            release.version.major for release in self.releases
        }
        if len(all_versions) != 1:
            msg = (
                f"Family contains more than one major version: {all_versions}."
            )
            raise IncompatibleFamilyError(msg)

    @property
    def supported(self) -> bool:
        """Return if this family is currently supported."""
        return any(version.supported for version in self.releases)

    @property
    def version(self) -> int:
        """Return the version identifier of this family."""
        semantic_version: SemanticVersion = self.releases[0].version
        return semantic_version.major


class IncompatibleFamilyError(Exception):
    """Exception that is raised when a Nuke Family is incompatible."""

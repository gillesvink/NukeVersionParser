"""Datamodel that is able to store all data related to Nuke versions.

@maintainer: Gilles Vink
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class NukeInstaller:
    """Data related to a link to a Nuke version."""

    mac_x86_64: str
    """URL to the Mac installer."""
    linux_x86_64: str
    """URL to the Linux installer."""
    windows_x86_64: str
    """URL to the Windows installer."""
    mac_arm: str = None
    """URL to the Mac ARM (M1, M2..) installer.
    Note: only supported from Nuke 15+"""


@dataclass
class NukeVersion:
    """Data related to a specific Nuke Version."""

    major: int
    """Major version."""
    minor: int
    """Feature improvement."""
    version: int
    """Bugfix release"""
    supported: bool
    """True if still maintained, False if not."""
    date: str
    """Date of release."""
    installer: NukeInstaller
    """Installer data."""


@dataclass
class NukeFamily:
    """Data containing everything related to a family of Nuke versions."""

    versions: list[NukeVersion]

    def __post_init__(self) -> None:
        """Check if provided NukeVersions are compatible.

        Raises:
            IncompatibleFamilyError: if versions are not the same major.
        """
        all_versions = {nuke_version.version for nuke_version in self.versions}
        if len(all_versions) != 1:
            msg = (
                f"Family contains more than one major version: {all_versions}."
            )
            raise IncompatibleFamilyError(msg)

    @property
    def supported(self) -> bool:
        """Return if this family is currently supported."""
        return any(version.supported for version in self.versions)

    @property
    def version(self) -> int:
        """Return the version identifier of this family."""
        return self.versions[0].version


class IncompatibleFamilyError(Exception):
    """Exception that is raised when a Nuke Family is incompatible."""

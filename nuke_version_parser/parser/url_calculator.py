"""Script that handles the calculation of possible urls.

@maintainer: Gilles Vink
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from nuke_version_parser.datamodel.constants import (
    BASE_URL,
    Architecture,
    OperatingSystem,
)

if TYPE_CHECKING:
    from nuke_version_parser.datamodel.nuke_data import (
        SemanticVersion,
    )


def _get_architecture_formatting(
    architecture: Architecture, old_format: bool | None = None
) -> str:
    """Get the architecture formatting.

    There has been a change in naming from Nuke 11+, and ARM has been
    added with different naming too. Thats why we need a specific function
    for handling this.

    Args:
        architecture: the specific architecture that is requested
        old_format (optional): if old format is used. Defaults to None.

    Returns:
        architecture mapped to the expected format.
    """
    if architecture == Architecture.ARM:
        return f"{architecture.value}64"

    format_suffix = "-release-64" if old_format else "_64"
    return f"{architecture.value}{format_suffix}"


def _get_file_extension(operating_system: OperatingSystem) -> str:
    """Return the file extension corresponding to the OS.

    Args:
        operating_system: windows, linux or mac.

    Returns:
        corresponding file extension: either dmg, exe or tgz
    """
    if operating_system == OperatingSystem.WINDOWS:
        return "exe"
    if operating_system == OperatingSystem.MAC:
        return "dmg"
    return "tgz"


def calculate_url(
    version: SemanticVersion,
    system: OperatingSystem,
    architecture: Architecture,
    old_format: bool | None = None,
) -> str:
    """Calculate external url based on provided data.

    Note:
        This function might produce a url that does not exists.
        It does not check anything on the internet.

    Args:
        version: semantic version related to version
        system: used operating system, linux, mac or windows.
        architecture: arm or x86
        old_format (optional: use old format for url. Defaults to None.

    Returns:
        calculated possible url
    """
    calculated_architecture = _get_architecture_formatting(
        architecture=architecture, old_format=old_format
    )
    file_extension = _get_file_extension(operating_system=system)

    return BASE_URL.format(
        major=version.major,
        minor=version.minor,
        patch=version.patch,
        os=system.value,
        architecture=calculated_architecture,
        extension=file_extension,
    )

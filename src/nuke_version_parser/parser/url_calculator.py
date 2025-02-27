"""Script that handles the calculation of possible urls.

@maintainer: Gilles Vink
"""
from __future__ import annotations

from nuke_version_parser.datamodel.constants import (
    BASE_URL,
    Architecture,
    OperatingSystem,
)
from nuke_version_parser.datamodel.nuke_data import (
    SemanticVersion,
)


def _get_architecture_formatting(
    architecture: Architecture,
    version: SemanticVersion,
) -> str:
    """Get the architecture formatting.

    There has been a change in naming from Nuke 11+, and ARM has been
    added with different naming too. Thats why we need a specific function
    for handling this.

    Args:
        architecture: the specific architecture that is requested
        version: to determine if old formatting should be used

    Returns:
        architecture mapped to the expected format.
    """
    if architecture == Architecture.ARM:
        return f"{architecture.value}64"
    format_suffix = "_64"
    if version < SemanticVersion(12, 0, 2):
        format_suffix = "-release-64"
    elif _uses_temporary_naming(version):
        format_suffix = "-64-installer"
    return f"{architecture.value}{format_suffix}"


def _get_file_extension(operating_system: OperatingSystem) -> str:
    """Return the file extension corresponding to the OS.

    Args:
        operating_system: windows, linux or mac.

    Returns:
        corresponding file extension: either dmg, exe or tgz
    """
    if operating_system == OperatingSystem.WINDOWS:
        return "zip"
    if operating_system == OperatingSystem.MAC:
        return "dmg"
    return "tgz"


def _uses_temporary_naming(version: SemanticVersion) -> bool:
    """This was naming introduced in Nuke 12 and partially 13.

    This function checks if the version is applicable for that naming.

    Args:
        version: version to check for.

    Returns:
        True if temporary naming applies, False if not.
    """
    if version > SemanticVersion(13, 0, 0) and version < SemanticVersion(
        13, 0, 3
    ):
        return True
    if version > SemanticVersion(12, 0, 1) and version < SemanticVersion(
        12, 2, 7
    ):
        return True
    return False


def calculate_url(
    version: SemanticVersion,
    system: OperatingSystem,
    architecture: Architecture,
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
        version=version, architecture=architecture
    )
    file_extension = _get_file_extension(operating_system=system)
    version_separator = "" if not _uses_temporary_naming(version) else "-"
    return BASE_URL.format(
        major=version.major,
        version_separator=version_separator,
        minor=version.minor,
        patch=version.patch,
        os=system.value,
        architecture=calculated_architecture,
        extension=file_extension,
    )

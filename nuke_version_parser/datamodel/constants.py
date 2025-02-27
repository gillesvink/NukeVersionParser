"""Constants related to the version parser.

@maintainer: Gilles Vink
"""

from enum import Enum


class OperatingSystem(str, Enum):
    """Available operating systems, and mapped to their shortname."""

    MAC: str = "mac"
    LINUX: str = "linux"
    WINDOWS: str = "win"


class Architecture(str, Enum):
    """Current processor architectures."""

    X86_64: str = "x86"
    ARM: str = "arm"


BASE_URL: str = (
    "https://thefoundry.s3.amazonaws.com/products/nuke/releases/"
    "{major}.{minor}v{patch}/"
    "Nuke{version_separator}{major}.{minor}v{patch}-{os}-"
    "{architecture}.{extension}"
)
"""Structure of a base url where the executables are stored."""

"""Tests related to the URL calculator.

@maintainer: Gilles Vink
"""

import pytest

from nuke_version_parser.datamodel.constants import (
    Architecture,
    OperatingSystem,
)
from nuke_version_parser.datamodel.nuke_data import SemanticVersion
from nuke_version_parser.parser.url_calculator import calculate_url


@pytest.mark.parametrize(
    ("version", "system", "architecture", "expected_url"),
    [
        (
            SemanticVersion(10, 0, 1),
            OperatingSystem.LINUX,
            Architecture.X86,
            "https://thefoundry.s3.amazonaws.com/products/nuke/releases/10.0v1/Nuke10.0v1-linux-x86-release-64.tgz",
        ),
        (
            SemanticVersion(13, 3, 2),
            OperatingSystem.LINUX,
            Architecture.X86,
            "https://thefoundry.s3.amazonaws.com/products/nuke/releases/13.3v2/Nuke13.3v2-linux-x86_64.tgz",
        ),
        (
            SemanticVersion(13, 3, 2),
            OperatingSystem.MAC,
            Architecture.X86,
            "https://thefoundry.s3.amazonaws.com/products/nuke/releases/13.3v2/Nuke13.3v2-mac-x86_64.dmg",
        ),
        (
            SemanticVersion(13, 3, 2),
            OperatingSystem.MAC,
            Architecture.ARM,
            "https://thefoundry.s3.amazonaws.com/products/nuke/releases/13.3v2/Nuke13.3v2-mac-arm64.dmg",
        ),
        (
            SemanticVersion(13, 3, 2),
            OperatingSystem.WINDOWS,
            Architecture.X86,
            "https://thefoundry.s3.amazonaws.com/products/nuke/releases/13.3v2/Nuke13.3v2-win-x86_64.zip",
        ),
        (
            SemanticVersion(13, 0, 3),
            OperatingSystem.WINDOWS,
            Architecture.X86,
            "https://thefoundry.s3.amazonaws.com/products/nuke/releases/13.0v3/Nuke13.0v3-win-x86_64.zip",
        ),
        (
            SemanticVersion(13, 0, 2),
            OperatingSystem.LINUX,
            Architecture.X86,
            "https://thefoundry.s3.amazonaws.com/products/nuke/releases/13.0v2/Nuke-13.0v2-linux-x86-64-installer.tgz",
        ),
        (
            SemanticVersion(12, 0, 2),
            OperatingSystem.LINUX,
            Architecture.X86,
            "https://thefoundry.s3.amazonaws.com/products/nuke/releases/12.0v2/Nuke-12.0v2-linux-x86-64-installer.tgz",
        ),
        (
            SemanticVersion(12, 0, 1),
            OperatingSystem.LINUX,
            Architecture.X86,
            "https://thefoundry.s3.amazonaws.com/products/nuke/releases/12.0v1/Nuke12.0v1-linux-x86-release-64.tgz",
        ),
    ],
)
def test_url_calculator(
    version, system, architecture, expected_url
) -> None:
    """Test the url calculator to correspond with the expected url."""
    assert (
        calculate_url(
            version=version,
            system=system,
            architecture=architecture,
        )
        == expected_url
    )

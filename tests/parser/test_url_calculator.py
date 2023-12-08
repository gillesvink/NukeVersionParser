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
    ("system", "architecture", "old_format", "expected_url"),
    [
        (
            OperatingSystem.LINUX,
            Architecture.X86,
            True,
            "https://thefoundry.s3.amazonaws.com/products/nuke/releases/10.3v2/Nuke10.3v2-linux-x86-release-64.tgz",
        ),
        (
            OperatingSystem.LINUX,
            Architecture.X86,
            False,
            "https://thefoundry.s3.amazonaws.com/products/nuke/releases/10.3v2/Nuke10.3v2-linux-x86_64.tgz",
        ),
        (
            OperatingSystem.MAC,
            Architecture.X86,
            False,
            "https://thefoundry.s3.amazonaws.com/products/nuke/releases/10.3v2/Nuke10.3v2-mac-x86_64.dmg",
        ),
        (
            OperatingSystem.MAC,
            Architecture.ARM,
            False,
            "https://thefoundry.s3.amazonaws.com/products/nuke/releases/10.3v2/Nuke10.3v2-mac-arm64.dmg",
        ),
        (
            OperatingSystem.WINDOWS,
            Architecture.X86,
            False,
            "https://thefoundry.s3.amazonaws.com/products/nuke/releases/10.3v2/Nuke10.3v2-win-x86_64.exe",
        ),
    ],
)
def test_url_calculator(
    system, architecture, old_format, expected_url
) -> None:
    """Test the url calculator to correspond with the expected url."""
    semantic_version = SemanticVersion(10, 3, 2)
    assert (
        calculate_url(
            version=semantic_version,
            system=system,
            architecture=architecture,
            old_format=old_format,
        )
        == expected_url
    )

"""Tests related to the version datamodel.

@maintainer: Gilles Vink
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from nuke_version_parser.datamodel.nuke_data import (
    IncompatibleFamilyError,
    NukeFamily,
    NukeRelease,
    SemanticVersion,
)


class TestNukeFamily:
    """Tests related to the NukeFamily data object."""

    DUMMY_VERSION = SemanticVersion(1, 2, 3)

    @pytest.mark.parametrize(
        ("test_supported_values", "expected_supported"),
        [
            ([False], False),
            ([True, False], True),
            ([True], True),
            ([False, False, True, False], True),
        ],
    )
    def test_supported(
        self, test_supported_values: list[bool], expected_supported
    ) -> None:
        """Test that the supported property corresponds to the data."""
        test_nuke_versions = [
            MagicMock(
                spec=NukeRelease,
                supported=supported,
                version=self.DUMMY_VERSION,
                date=None,
            )
            for supported in test_supported_values
        ]
        assert NukeFamily(test_nuke_versions).supported == expected_supported

    def test_raise_exception_with_incompatible_versions(self) -> None:
        """Test to raise an IncompatibleFamily during differing versions."""
        all_versions = [SemanticVersion(14, 1, 2), SemanticVersion(15, 1, 2)]
        test_nuke_versions = [
            MagicMock(spec=NukeRelease, version=version, date=None)
            for version in all_versions
        ]

        with pytest.raises(IncompatibleFamilyError):
            NukeFamily(test_nuke_versions)

    @pytest.mark.parametrize(
        ("test_versions", "expected_version"),
        [
            ([SemanticVersion(15, 1, 1), SemanticVersion(15, 2, 3)], 15),
            ([SemanticVersion(12, 1, 1), SemanticVersion(12, 2, 3)], 12),
        ],
    )
    def test_retrieve_version(
        self, test_versions: list[int], expected_version: int
    ) -> None:
        """Test that from a list of int, the correct version is retrieved."""
        test_nuke_versions = [
            MagicMock(spec=NukeRelease, version=version, date=None)
            for version in test_versions
        ]

        test_family = NukeFamily(test_nuke_versions)

        assert test_family.version == expected_version

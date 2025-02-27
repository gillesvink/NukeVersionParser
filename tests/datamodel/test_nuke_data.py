"""Tests related to the version datamodel.

@maintainer: Gilles Vink
"""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from nukeversionparser.datamodel.nuke_data import (
    IncompatibleFamilyError,
    NukeFamily,
    NukeInstaller,
    NukeRelease,
    SemanticVersion,
)


class TestSemanticVersion:
    """Tests related to the SemanticVersion object."""

    @staticmethod
    def test_to_string() -> None:
        """Test conversion to string to return version format in 1.0v1."""
        assert str(SemanticVersion(1, 0, 1)) == "1.0v1"

    @staticmethod
    @pytest.mark.parametrize(
        ("first_version", "second_version", "first_is_newer_than_second"),
        [
            (SemanticVersion(1, 0, 2), SemanticVersion(1, 0, 1), True),
            (SemanticVersion(1, 1, 1), SemanticVersion(1, 0, 1), True),
            (SemanticVersion(2, 0, 1), SemanticVersion(1, 0, 1), True),
            (SemanticVersion(1, 1, 1), SemanticVersion(1, 1, 3), False),
            (SemanticVersion(1, 11, 20), SemanticVersion(10, 0, 3), False),
            (SemanticVersion(19, 0, 1), SemanticVersion(1, 30, 511), True),
        ],
    )
    def test_size_comparison(
        first_version: SemanticVersion,
        second_version: SemanticVersion,
        first_is_newer_than_second: bool,
    ) -> None:
        """Test comparisons to report if one version is larger or not."""
        assert (first_version > second_version) == first_is_newer_than_second
        inversed_result = not first_is_newer_than_second
        assert (first_version < second_version) == inversed_result

    @staticmethod
    def test_size_comparison_with_equal_data() -> None:
        """Test to make sure equal data will always return False."""
        assert (SemanticVersion(1, 0, 1) < SemanticVersion(1, 0, 1)) == False
        assert (SemanticVersion(1, 0, 1) > SemanticVersion(1, 0, 1)) == False

    @staticmethod
    def test_size_comparison_with_invalid_object() -> None:
        """Test to raise a TypeError when compared to an invalid object."""
        with pytest.raises(
            TypeError,
            match="Comparison only allowed to SemanticVersion object.",
        ):
            SemanticVersion(1, 2, 3) > 1


class TestNukeRelease:
    """Tests related to the NukeRelease object."""

    @staticmethod
    def test_to_dict() -> None:
        """Test that we get a dict in our expected format."""
        test_release = NukeRelease(
            version=SemanticVersion(1, 0, 1),
            installer=NukeInstaller(
                linux_x86_64="some url", windows_x86_64="another url"
            ),
            date="my date",
        )
        expected_dict = {
            "1.0v1": {
                "installer": {
                    "linux_x86_64": "some url",
                    "mac_arm": None,
                    "mac_x86_64": None,
                    "windows_x86_64": "another url",
                },
                "date": "my date",
                "supported": True,
            }
        }
        with patch(
            "nukeversionparser.datamodel.nuke_data.NukeRelease.get_supported",
            return_value=True,
        ):
            converted_result = test_release.to_dict()

        assert converted_result == expected_dict

    @staticmethod
    @pytest.mark.parametrize(
        ("test_date", "expected_supported"),
        [
            ("Tue, 31 Dec 2019 00:00:00 GMT", True),
            ("Sun, 31 Dec 2017 00:00:00 GMT", False),
            ("Sat, 30 Jun 2018 00:00:00 GMT", False),
            ("Sat, 30 Jul 2018 00:00:01 GMT", True),
            ("Mon, 1 Jan 2024 00:00:00 GMT", True),
        ],
    )
    def test_supported(test_date: str, expected_supported: bool) -> None:
        """Test the supported property to return the supported bool.

        After 18 months, the release is unsupported. Thus returning
        False. If it is released within 18 months, this should return
        True.

        Note:
            This test expects this day is 01/01/2020 (pre corona D:)
        """
        test_current_date = datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        test_release = NukeRelease(
            version=None, installer=None, date=test_date
        )
        with patch(
            "nukeversionparser.datamodel.nuke_data.datetime", wraps=datetime
        ) as datetime_mock:
            datetime_mock.now.return_value = test_current_date
            assert test_release.get_supported() == expected_supported

    @staticmethod
    def test_supported_with_no_date_set() -> None:
        """Test to raise a ValueError if no date is set."""
        with pytest.raises(
            ValueError, match="No date is set, can't get supported state."
        ):
            NukeRelease(
                version=None, installer=None, date=None
            ).get_supported()


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
        test_nuke_versions = []
        for supported in test_supported_values:
            release_mock = MagicMock(
                spec=NukeRelease, version=self.DUMMY_VERSION
            )
            release_mock.get_supported.return_value = supported
            test_nuke_versions.append(release_mock)
        assert (
            NukeFamily(test_nuke_versions).get_supported()
            == expected_supported
        )

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

    def test_to_dict(self) -> None:
        """Test to return dict using major version and provided dict."""
        test_release = MagicMock(
            spec=NukeRelease, version=SemanticVersion(15, 0, 1)
        )
        test_release.get_supported.return_value = True
        test_release.to_dict.return_value = {"15.0v1": {"some": "data"}}
        test_family = NukeFamily([test_release])

        assert test_family.to_dict() == {15: {"15.0v1": {"some": "data"}}}
        test_release.to_dict.assert_called_once()

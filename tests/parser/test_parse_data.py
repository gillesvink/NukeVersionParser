"""Tests related to the parsing functionality.

@maintainer: Gilles Vink
"""
from __future__ import annotations

from dataclasses import fields
from unittest.mock import MagicMock, patch

import pytest
from requests import Response

from nuke_version_parser.datamodel.constants import (
    Architecture,
    OperatingSystem,
)
from nuke_version_parser.datamodel.nuke_data import (
    NukeInstaller,
    NukeRelease,
    SemanticVersion,
)
from nuke_version_parser.parser.parse_data import (
    _parse_release_data_by_attribute,
    _VersionParser,
)


@pytest.fixture(autouse=True)
def _requests_mock() -> None:
    """Make sure we actually don't make any requests."""
    response_mock = MagicMock(spec=Response)
    response_mock.status_code = 200
    response_mock.headers = {"last-modified": "test_date"}

    requests_patch = patch(
        "nuke_version_parser.parser.parse_data.requests.head",
        return_value=response_mock,
    )

    with requests_patch:
        yield


class TestVersionParser:
    """Tests related to the version parser object."""

    @pytest.mark.parametrize("data_exists", [True, False])
    def test_retrieve_data(self, data_exists: bool) -> None:
        """Test to retrieve None with code 403 and str with code 200."""
        version_parser = _VersionParser(SemanticVersion(1, 0, 0))
        response_mock = MagicMock(spec=Response)
        response_mock.headers = {"last-modified": "test_date"}
        response_mock.status_code = 200 if data_exists else 403

        with patch(
            "nuke_version_parser.parser.parse_data.calculate_url"
        ) as url_calculator_mock, patch(
            "nuke_version_parser.parser.parse_data.requests.head",
            return_value=response_mock,
        ):
            retrieved_data = version_parser.retrieve_data(
                OperatingSystem.LINUX, Architecture.X86
            )

        url_calculator_mock.assert_called_once_with(
            version=SemanticVersion(1, 0, 0),
            system=OperatingSystem.LINUX,
            architecture=Architecture.X86,
        )
        if data_exists:
            assert retrieved_data
        else:
            assert not retrieved_data

    @pytest.mark.parametrize("data_exists", [True, False])
    def test_retrieve_data_store_date(self, data_exists: bool) -> None:
        """Test that date is stored when data is available."""
        version_parser = _VersionParser(SemanticVersion(1, 0, 0))
        response_mock = MagicMock(spec=Response)
        response_mock.status_code = 200 if data_exists else 403
        response_mock.headers = {"last-modified": "test_date"}
        with patch(
            "nuke_version_parser.parser.parse_data.requests.head",
            return_value=response_mock,
        ):
            version_parser.retrieve_data(
                OperatingSystem.LINUX, Architecture.X86
            )

        if data_exists:
            assert version_parser.date == "test_date"
        else:
            assert version_parser.date == None

    @pytest.mark.parametrize("data_exists", [True, False])
    def test_to_nuke_release(self, data_exists: bool) -> None:
        """Test to iterate over all data and return NukeRelease."""
        response_mock = MagicMock(spec=Response)
        response_mock.status_code = 200 if data_exists else 403
        response_mock.headers = {"last-modified": "test_date"}

        with patch(
            "nuke_version_parser.parser.parse_data.calculate_url"
        ) as url_calculator_mock, patch(
            "nuke_version_parser.parser.parse_data.requests.head",
            return_value=response_mock,
        ):
            retrieved_data = _VersionParser.to_nuke_release(
                SemanticVersion(1, 0, 0)
            )

        # make sure we have 4 unique calls
        assert len(url_calculator_mock.call_args_list) == len(
            fields(NukeInstaller)
        )
        if not data_exists:
            assert retrieved_data is None
            return
        assert isinstance(retrieved_data, NukeRelease)
        assert retrieved_data.date == "test_date"
        assert retrieved_data.version == SemanticVersion(1, 0, 0)
        assert isinstance(retrieved_data.installer, NukeInstaller)


class TestParseReleaseDataByAttribute:
    """Tests related to the parse_release_data_by_attribute function."""

    @pytest.mark.parametrize(
        ("attribute_name", "expected_calls"),
        [
            (
                "major",
                [SemanticVersion(1, 0, 0), SemanticVersion(2, 0, 0)],
            ),
            (
                "minor",
                [SemanticVersion(1, 0, 0), SemanticVersion(1, 1, 0)],
            ),
            (
                "patch",
                [SemanticVersion(1, 0, 0), SemanticVersion(1, 0, 1)],
            ),
        ],
    )
    def test_iterating_over_specified_attribute(
        self, attribute_name: str, expected_calls: list[SemanticVersion]
    ) -> None:
        """Test iteration over attribute stops after None."""
        with patch(
            "nuke_version_parser.parser.parse_data._VersionParser.to_nuke_release"
        ) as version_parser_mock:
            version_parser_mock.side_effect = [
                "first_data",
                "second_data",
                None,
            ]
            _parse_release_data_by_attribute(
                SemanticVersion(1, 0, 0), attribute_name
            )

        assert version_parser_mock.call_count == 3
        version_parser_mock.assert_any_call(expected_calls[0])
        version_parser_mock.assert_any_call(expected_calls[1])


# class TestParseAllData:
#     """Tests related to the parse_all_data function."""

#     @pytest.fixture()
#     def release_parser_mock(self) -> MagicMock:
#         """Mock to set the status code"""
#         with patch(
#             "nuke_version_parser.parser.parse_data.requests.response.status_code"
#         ) as status_code_mock:
#             yield status_code_mock

#     def test__get_all_families(self, version_parser_mock) -> None:
#         """Test to retrieve all existing families."""

#         for family in families:
#         assert collected_versions == {

"""Tests related to the export data script.

@maintainer: Gilles Vink
"""


import copy
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from nukeversionparser.datamodel.nuke_data import (
    NukeFamily,
    NukeRelease,
    SemanticVersion,
)
from nukeversionparser.exporter.export_data import (
    _convert_data_to_json,
    _create_all_json,
    _create_all_supported_json,
    _create_minor_json,
    _create_minor_supported_json,
    _reduce_to_only_minor_releases,
    _reduce_to_only_supported,
    _sort_families,
    _write_json_to_file,
)


def test__sort_releases() -> None:
    """Test to make sure output is sorted by latest versions.

    This means, in order of importance:
    latest major -> latest minor -> latest patch
    """
    test_unsorted_list = [
        NukeFamily(
            [
                NukeRelease(
                    SemanticVersion(10, 1, 3), installer=None, date=None
                ),
                NukeRelease(
                    SemanticVersion(10, 0, 4), installer=None, date=None
                ),
            ]
        ),
        NukeFamily(
            [
                NukeRelease(
                    SemanticVersion(9, 0, 2), installer=None, date=None
                ),
                NukeRelease(
                    SemanticVersion(9, 0, 1), installer=None, date=None
                ),
                NukeRelease(
                    SemanticVersion(9, 1, 1), installer=None, date=None
                ),
                NukeRelease(
                    SemanticVersion(9, 0, 3), installer=None, date=None
                ),
            ]
        ),
    ]
    expected_list = [
        NukeFamily(
            [
                NukeRelease(
                    SemanticVersion(10, 1, 3), installer=None, date=None
                ),
                NukeRelease(
                    SemanticVersion(10, 0, 4), installer=None, date=None
                ),
            ]
        ),
        NukeFamily(
            [
                NukeRelease(
                    SemanticVersion(9, 1, 1), installer=None, date=None
                ),
                NukeRelease(
                    SemanticVersion(9, 0, 3), installer=None, date=None
                ),
                NukeRelease(
                    SemanticVersion(9, 0, 2), installer=None, date=None
                ),
                NukeRelease(
                    SemanticVersion(9, 0, 1), installer=None, date=None
                ),
            ]
        ),
    ]

    assert test_unsorted_list != expected_list
    _sort_families(test_unsorted_list)
    assert test_unsorted_list == expected_list


def test__reduce_to_only_minor_releases() -> None:
    """Test convert to only contain minor releases.

    This will contain latest of patch of latest minor.
    """
    test_families = [
        NukeFamily(
            [
                NukeRelease(
                    SemanticVersion(9, 0, 1), installer=None, date=None
                ),
                NukeRelease(
                    SemanticVersion(9, 0, 2), installer=None, date=None
                ),
                NukeRelease(
                    SemanticVersion(9, 0, 3), installer=None, date=None
                ),
                NukeRelease(
                    SemanticVersion(9, 1, 1), installer=None, date=None
                ),
            ]
        ),
        NukeFamily(
            [
                NukeRelease(
                    SemanticVersion(10, 1, 3), installer=None, date=None
                ),
            ]
        ),
    ]
    expected_families = [
        NukeFamily(
            [
                NukeRelease(
                    SemanticVersion(9, 0, 3), installer=None, date=None
                ),
                NukeRelease(
                    SemanticVersion(9, 1, 1), installer=None, date=None
                ),
            ]
        ),
        NukeFamily(
            [
                NukeRelease(
                    SemanticVersion(10, 1, 3), installer=None, date=None
                ),
            ]
        ),
    ]

    _reduce_to_only_minor_releases(test_families)
    assert test_families == expected_families


def test__reduce_to_only_supported() -> None:
    """Test to keep only the supported releases in the provided list."""
    mock_release = MagicMock(
        spec=NukeRelease, version=SemanticVersion(1, 0, 1)
    )
    mock_release.get_supported.return_value = True

    supported_release = copy.deepcopy(mock_release)
    unsupported_release = copy.deepcopy(mock_release)
    unsupported_release.get_supported.return_value = False
    test_families = [
        NukeFamily([supported_release, unsupported_release]),
        NukeFamily(
            [
                unsupported_release,
            ]
        ),
    ]
    expected_result = [
        NukeFamily(
            [
                supported_release,
            ]
        ),
    ]

    _reduce_to_only_supported(test_families)

    assert test_families == expected_result


def test__convert_data_to_json() -> None:
    """Test to convert a list of NukeFamily to a JSON string."""
    first_nuke_family_mock = MagicMock(spec=NukeFamily)
    first_nuke_family_mock.to_dict.return_value = {"15": "first_data"}
    second_nuke_family_mock = MagicMock(spec=NukeFamily)
    second_nuke_family_mock.to_dict.return_value = {"16": "second_data"}
    test_families = [first_nuke_family_mock, second_nuke_family_mock]

    converted_data = _convert_data_to_json(test_families)

    assert converted_data == json.dumps(
        {"15": "first_data", "16": "second_data"}, indent=4
    )


def test__write_json_to_file(tmp_path: Path) -> None:
    """Test to write provided string to a file."""
    test_string = "my multiline \n string"
    test_file = tmp_path / "my_file.json"

    _write_json_to_file(json_data=test_string, file_path=test_file)

    assert test_file.read_text() == test_string


def test__write_json_to_file_to_raise_exception() -> None:
    """Test to raise an exception when the filepath is not a JSON file."""
    test_file = Path("something.txt")

    with pytest.raises(
        ValueError, match="Provided path does not end with .json"
    ):
        _write_json_to_file(json_data=None, file_path=test_file)


class TestDataCollectionAndReturning:
    """These tests simply exist for checking if implementation stays the same.

    All functions called within here have already been tested, so we only need
    to check if they have been called properly.
    """

    @staticmethod
    def test__create_all_json() -> None:
        """Test the creation of the all json data."""
        test_families = [MagicMock(spec=NukeFamily)]
        with patch(
            "nukeversionparser.exporter.export_data._convert_data_to_json"
        ) as convert_to_json_mock:
            result_data = _create_all_json(test_families)

        assert test_families is not result_data
        convert_to_json_mock.assert_called_once()

    @staticmethod
    def test__create_all_supported_json() -> None:
        """Test the creation of the all supported json data."""
        test_families = [MagicMock(spec=NukeFamily)]
        with patch(
            "nukeversionparser.exporter.export_data._convert_data_to_json"
        ) as convert_to_json_mock, patch(
            "nukeversionparser.exporter.export_data._reduce_to_only_supported"
        ) as reduce_mock:
            result_data = _create_all_supported_json(test_families)

        assert test_families is not result_data
        convert_to_json_mock.assert_called_once()
        reduce_mock.assert_called_once()

    @staticmethod
    def test__create_minor_json() -> None:
        """Test the creation of the minor releases json data."""
        test_families = [MagicMock(spec=NukeFamily)]
        with patch(
            "nukeversionparser.exporter.export_data._convert_data_to_json"
        ) as convert_to_json_mock, patch(
            "nukeversionparser.exporter.export_data._reduce_to_only_minor_releases"
        ) as convert_to_minor_mock:
            result_data = _create_minor_json(test_families)

        assert test_families is not result_data
        convert_to_json_mock.assert_called_once()
        convert_to_minor_mock.assert_called_once()

    @staticmethod
    def test__create_minor_supported_json() -> None:
        """Test the creation of the minor supported releases json data."""
        test_families = [MagicMock(spec=NukeFamily)]
        with patch(
            "nukeversionparser.exporter.export_data._convert_data_to_json"
        ) as convert_to_json_mock, patch(
            "nukeversionparser.exporter.export_data._reduce_to_only_supported"
        ) as reduce_mock, patch(
            "nukeversionparser.exporter.export_data._reduce_to_only_minor_releases"
        ) as convert_to_minor_mock:
            result_data = _create_minor_supported_json(test_families)

        assert test_families is not result_data
        convert_to_json_mock.assert_called_once()
        reduce_mock.assert_called_once()
        convert_to_minor_mock.assert_called_once()

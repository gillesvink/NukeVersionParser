"""Test script related to the family collector.

@maintainer: Gilles Vink
"""


from unittest.mock import patch

from nuke_version_parser.datamodel.nuke_data import (
    NukeFamily,
    NukeRelease,
    SemanticVersion,
)
from nuke_version_parser.parser.collector import (
    _find_all_minor_versions,
    _find_all_patch_versions,
    _get_all_families,
    collect_families,
)


def test__get_all_families() -> None:
    """Test to retrieve all existing families."""
    release_1 = NukeRelease(
        version=SemanticVersion(1, 0, 1), installer=None, date=None
    )
    release_2 = NukeRelease(
        version=SemanticVersion(2, 0, 1), installer=None, date=None
    )
    expected_families = [NukeFamily([release_1]), NukeFamily([release_2])]

    with patch(
        "nuke_version_parser.parser.collector.parse_release_data_by_attribute"
    ) as version_parser_mock:
        version_parser_mock.return_value = [
            release_1,
            release_2,
        ]
        collected_families = _get_all_families()

    assert collected_families == expected_families


def test__find_all_minor_versions() -> None:
    """Test find all minor versions to find new versions from family."""
    already_found_release = NukeRelease(
        version=SemanticVersion(1, 0, 1), installer=None, date=None
    )
    test_family = NukeFamily([already_found_release])
    new_release_2 = NukeRelease(
        version=SemanticVersion(1, 1, 1), installer=None, date=None
    )
    new_release_3 = NukeRelease(
        version=SemanticVersion(1, 2, 1), installer=None, date=None
    )
    expected_family = NukeFamily(
        [already_found_release, new_release_2, new_release_3]
    )

    with patch(
        "nuke_version_parser.parser.collector.parse_release_data_by_attribute"
    ) as version_parser_mock:
        version_parser_mock.return_value = [
            new_release_2,
            new_release_3,
        ]
        _find_all_minor_versions(test_family)

    assert test_family == expected_family


def test__find_all_patch_versions() -> None:
    """Test find all patch versions to find new versions from family."""
    already_found_release = NukeRelease(
        version=SemanticVersion(1, 0, 1), installer=None, date=None
    )
    test_family = NukeFamily([already_found_release])
    new_release_2 = NukeRelease(
        version=SemanticVersion(1, 0, 2), installer=None, date=None
    )
    new_release_3 = NukeRelease(
        version=SemanticVersion(1, 0, 3), installer=None, date=None
    )
    expected_family = NukeFamily(
        [already_found_release, new_release_2, new_release_3]
    )

    with patch(
        "nuke_version_parser.parser.collector.parse_release_data_by_attribute"
    ) as version_parser_mock:
        version_parser_mock.return_value = [
            new_release_2,
            new_release_3,
        ]
        _find_all_patch_versions(test_family)

    assert test_family == expected_family


def test_collect_families() -> None:
    """Test collect to iterate over found families and call functions."""
    family1 = NukeFamily(
            [
                NukeRelease(
                    version=SemanticVersion(9, 0, 1),
                    installer=None,
                    date=None,
                )
            ],
        )
    family2 = NukeFamily(
            [
                NukeRelease(
                    version=SemanticVersion(10, 0, 1),
                    installer=None,
                    date=None,
                )
            ]
        )
    major_families = [family1, family2]

    with patch(
        "nuke_version_parser.parser.collector._get_all_families",
        return_value=major_families,
    ) as get_families_mock, patch(
        "nuke_version_parser.parser.collector._find_all_minor_versions",
    ) as find_minor_mock, patch(
        "nuke_version_parser.parser.collector._find_all_patch_versions",
    ) as find_patch_mock:
        collected_families = collect_families()

    get_families_mock.assert_called_once()
    assert collected_families
    for family in collected_families:
        assert isinstance(family, NukeFamily)
    for family in [family1, family2]:
        find_minor_mock.assert_any_call(family)
        find_patch_mock.assert_any_call(family)


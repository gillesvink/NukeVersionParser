"""Tests related to the export data script.

@maintainer: Gilles Vink
"""


from nuke_version_parser.datamodel.nuke_data import (
    NukeFamily,
    NukeRelease,
    SemanticVersion,
)


def test__convert_to_only_major_releases() -> None:
    """Test convert to only contain major releases.

    This will contain latest of patch of latest minor.
    """
    test_families = [
        NukeFamily(
            [
                NukeRelease(SemanticVersion(9, 0, 1)),
                NukeRelease(SemanticVersion(9, 0, 2)),
                NukeRelease(SemanticVersion(9, 0, 3)),
                NukeRelease(SemanticVersion(9, 1, 1)),
            ]
        ),
        NukeFamily(
            [
                NukeRelease(SemanticVersion(10, 1, 3)),
            ]
        ),
    ]
    expected_families = [
        NukeFamily(
            [
                NukeRelease(SemanticVersion(9, 0, 3)),
                NukeRelease(SemanticVersion(9, 1, 1)),
            ]
        ),
        NukeFamily(
            [
                NukeRelease(SemanticVersion(10, 1, 3)),
            ]
        ),
    ]

    test_result = _convert_to_only_major_releases(test_families)
    
    assert test_result == expected_families


def test__sort_releases() -> None:
    """Test to make sure output is sorted by latest versions.

    This means, in order of importance:
    latest major -> latest minor -> latest patch
    """
"""General test configuration.

@maintainer: Gilles Vink
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from requests import Response


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


@pytest.fixture(autouse=True)
def _current_time_mock() -> None:
    """Make sure the tests run in the same time each time."""
    current_date = datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    with patch(
        "nuke_version_parser.datamodel.nuke_data.datetime", wraps=datetime
    ) as time_mock:
        time_mock.now.return_value = current_date
        yield

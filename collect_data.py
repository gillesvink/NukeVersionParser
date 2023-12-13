"""Script that is responsible executing the collecting.

@maintainer: Gilles Vink
"""

import logging
import os
from pathlib import Path

from nuke_version_parser.exporter.export_data import (
    collect_and_write_json_files,
)

FORMAT = "[%(asctime)s] %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)


def run_collector() -> None:
    """Execute the collector to collect Nuke releases data.

    Raises:
        RuntimeError: if no JSON_WRITE_DIRECTORY environment is set.
    """
    write_directory = os.getenv("JSON_WRITE_DIRECTORY")
    if not write_directory:
        msg = "No write directory specified, set the JSON_WRITE_DIRECTORY env."
        raise RuntimeError(msg)
    json_directory = Path(write_directory)
    collect_and_write_json_files(json_directory)


if __name__ == "__main__":
    run_collector

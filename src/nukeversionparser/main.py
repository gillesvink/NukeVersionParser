"""Script that is responsible executing the collecting.

@maintainer: Gilles Vink
"""

import argparse
import logging
import sys
from pathlib import Path

from nukeversionparser.exporter.export_data import (
    collect_and_write_json_files,
)

FORMAT = "[%(asctime)s] %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)


def _parse_args(args: list[str]) -> argparse.Namespace:
    """Parse provided arguments."""
    parser = argparse.ArgumentParser(
        prog="NukeVersionParser",
        description=("CLI to fetch all Nuke versions and write result to JSON."),
    )
    parser.add_argument("--write_dir", required=True)
    return parser.parse_args(args)


def main() -> None:
    """Main pytest bootstrap entrypoint"""
    parsed_arguments = _parse_args(sys.argv[1:])
    if parsed_arguments.write_dir is None:
        msg = (
            "Provide the path to write to. For example: "
            "nuke-versionparser ./ for the current directory."
        )
        raise ValueError(msg)
    json_directory = Path(parsed_arguments.write_dir)
    collect_and_write_json_files(json_directory)


if __name__ == "__main__":
    main()

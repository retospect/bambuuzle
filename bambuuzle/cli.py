"""Command-line interface for bambuuzle."""

from __future__ import annotations

import argparse
import sys

from .bambu_file import BambuFile


def get_plate(args: argparse.Namespace) -> None:
    """Extract a plate's gcode from a .gcode.3mf file."""
    bf = BambuFile.open(args.file)
    plate = bf.plate(args.plate)
    output = f"plate_{args.plate}.gcode"
    with open(output, "w") as f:
        f.write(plate.gcode)
    print(f"Extracted plate {args.plate} -> {output} ({len(plate.gcode)} bytes)")


def put_plate(args: argparse.Namespace) -> None:
    """Insert a plate's gcode into a .gcode.3mf file."""
    bf = BambuFile.open(args.file)
    gcode_file = f"plate_{args.plate}.gcode"
    with open(gcode_file, "r") as f:
        gcode = f.read()

    try:
        plate = bf.plate(args.plate)
        plate.gcode = gcode
    except KeyError:
        bf.add_plate(gcode=gcode, number=args.plate)

    output = args.output or args.file
    bf.save(output)
    print(f"Inserted {gcode_file} -> {output}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="bambuuzle",
        description="Extract and re-insert gcode from Bambu .gcode.3mf files",
    )
    subparsers = parser.add_subparsers(dest="command")

    # get_plate
    gp = subparsers.add_parser("get_plate", help="Extract plate gcode to a file")
    gp.add_argument("file", help="Input .gcode.3mf file")
    gp.add_argument(
        "--plate", type=int, default=1, help="Plate number (default: 1)"
    )
    gp.set_defaults(func=get_plate)

    # put_plate
    pp = subparsers.add_parser("put_plate", help="Insert plate gcode from a file")
    pp.add_argument("file", help="Input .gcode.3mf file")
    pp.add_argument(
        "--plate", type=int, default=1, help="Plate number (default: 1)"
    )
    pp.add_argument(
        "--output", "-o", help="Output file (default: overwrite input)"
    )
    pp.set_defaults(func=put_plate)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)

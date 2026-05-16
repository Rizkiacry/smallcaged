from __future__ import annotations

import argparse
import sys

from smallcaged.fetcher import CHORD_TYPES, ROOT_TO_FILENAME, fetch_chord_file
from smallcaged.filter import is_valid_shape
from smallcaged.parser import parse_chord_file
from smallcaged.render import render_chord_group


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Filter Howard's guitar chord shapes by playability rules"
    )
    parser.add_argument(
        "--chord", "-c",
        default=None,
        help="Chord type filter (e.g. 'm', '7', 'maj7'). Default: all.",
    )
    parser.add_argument(
        "--root", "-r",
        default=None,
        help="Root note filter (e.g. 'C', 'G#'). Default: all 12 roots.",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output file. Default: stdout.",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Re-download cached files.",
    )
    args = parser.parse_args(argv)

    if args.root and args.root not in ROOT_TO_FILENAME:
        print(f"error: unknown root '{args.root}'. Use --help for valid roots.", file=sys.stderr)
        return 1

    roots = [args.root] if args.root else sorted(ROOT_TO_FILENAME.keys(), key=_root_sort_key)
    chord_types = [args.chord] if args.chord else CHORD_TYPES

    output_lines: list[str] = []

    for root in roots:
        for chord_type in chord_types:
            text = fetch_chord_file(root, chord_type, force=args.refresh)
            if text is None:
                continue
            shapes = parse_chord_file(root, chord_type, text)
            valid = [s for s in shapes if is_valid_shape(s)]
            if valid:
                output_lines.append(render_chord_group(root, chord_type, valid))

    output = "\n".join(output_lines)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
    else:
        sys.stdout.write(output)

    return 0


_NATURAL_ORDER = {
    "C": 0, "C#": 1, "Db": 1,
    "D": 2, "D#": 3, "Eb": 3,
    "E": 4,
    "F": 5, "F#": 6, "Gb": 6,
    "G": 7, "G#": 8, "Ab": 8,
    "A": 9, "A#": 10, "Bb": 10,
    "B": 11,
}


def _root_sort_key(root: str) -> int:
    return _NATURAL_ORDER.get(root, 99)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Convert a JSON array of objects to CSV.

Reads JSON from a file or stdin and writes CSV to stdout.
Column order is the order keys first appear in the input, unless
--columns is given. Nested values are JSON-encoded; --flatten expands
one level of nested objects into dotted keys (address.city).

Usage:
    json_to_csv.py [input.json] [--columns a,b,c] [--flatten]

Examples:
    json_to_csv.py users.json
    cat users.json | json_to_csv.py --columns name,email
    json_to_csv.py data.json --flatten > out.csv

Exit codes: 0 ok, 1 bad input (missing file, invalid JSON, not an
array of objects, empty array), 2 bad usage (--columns names an
unknown key, --flatten with a non-object value).
"""

import argparse
import csv
import json
import sys


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Convert a JSON array of objects to CSV."
    )
    parser.add_argument(
        "input", nargs="?", default="-",
        help="JSON file to read (default: stdin)",
    )
    parser.add_argument(
        "--columns", default=None,
        help="Comma-separated column names to output, in order",
    )
    parser.add_argument(
        "--flatten", action="store_true",
        help="Expand one level of nested objects into dotted keys",
    )
    return parser.parse_args(argv)


def load_rows(path):
    try:
        if path == "-":
            text = sys.stdin.read()
        else:
            with open(path, "r", encoding="utf-8") as fh:
                text = fh.read()
    except FileNotFoundError:
        print(f"json_to_csv: no such file: {path}", file=sys.stderr)
        return None
    except OSError as exc:
        print(f"json_to_csv: cannot read {path}: {exc}", file=sys.stderr)
        return None
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        print(f"json_to_csv: invalid JSON: {exc}", file=sys.stderr)
        return None
    if not isinstance(data, list):
        print("json_to_csv: top level must be a JSON array", file=sys.stderr)
        return None
    if not data:
        print("json_to_csv: empty array, nothing to convert", file=sys.stderr)
        return None
    for i, row in enumerate(data):
        if not isinstance(row, dict):
            print(
                f"json_to_csv: item {i} is not an object",
                file=sys.stderr,
            )
            return None
    return data


def flatten_row(row):
    flat = {}
    for key, value in row.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                flat[f"{key}.{sub_key}"] = sub_value
        else:
            flat[key] = value
    return flat


def encode(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return value


def main(argv=None):
    args = parse_args(argv)
    rows = load_rows(args.input)
    if rows is None:
        return 1

    if args.flatten:
        rows = [flatten_row(row) for row in rows]

    columns = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)

    if args.columns is not None:
        wanted = [c.strip() for c in args.columns.split(",") if c.strip()]
        unknown = [c for c in wanted if c not in columns]
        if unknown:
            print(
                "json_to_csv: unknown column(s): " + ", ".join(unknown),
                file=sys.stderr,
            )
            return 2
        columns = wanted

    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(columns)
    for row in rows:
        writer.writerow([encode(row.get(col)) for col in columns])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

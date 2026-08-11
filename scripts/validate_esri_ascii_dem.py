#!/usr/bin/env python3
"""Validate an ESRI ASCII grid, including files without NODATA_value."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


HEADER_KEYS = {
    "ncols",
    "nrows",
    "xllcorner",
    "yllcorner",
    "xllcenter",
    "yllcenter",
    "cellsize",
    "nodata_value",
}


def read_grid(path: Path) -> dict:
    lines = [line.strip() for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    header = {}
    position = 0
    while position < len(lines):
        parts = lines[position].split()
        key = parts[0].lower() if parts else ""
        if key not in HEADER_KEYS or len(parts) < 2:
            break
        header[key] = float(parts[1])
        position += 1

    required = ("ncols", "nrows", "cellsize")
    missing = [key for key in required if key not in header]
    if missing:
        raise ValueError("missing required header keys: " + ", ".join(missing))

    values = []
    for line in lines[position:]:
        values.extend(float(value) for value in line.split())

    ncols = int(header["ncols"])
    nrows = int(header["nrows"])
    expected = ncols * nrows
    nodata = header.get("nodata_value", -9999.0)
    valid = [value for value in values if not math.isclose(value, nodata, abs_tol=1e-9)]
    result = {
        "path": str(path.resolve()),
        "header_lines": position,
        "ncols": ncols,
        "nrows": nrows,
        "cellsize": header["cellsize"],
        "nodata_value": nodata,
        "has_explicit_nodata": "nodata_value" in header,
        "values_read": len(values),
        "values_expected": expected,
        "valid_values": len(valid),
        "valid_min": min(valid) if valid else None,
        "valid_max": max(valid) if valid else None,
    }

    xll = header.get("xllcorner", header.get("xllcenter"))
    yll = header.get("yllcorner", header.get("yllcenter"))
    if xll is not None and yll is not None:
        result["extent"] = {
            "xmin": xll,
            "ymin": yll,
            "xmax": xll + ncols * header["cellsize"],
            "ymax": yll + nrows * header["cellsize"],
        }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("asc", type=Path, help="ESRI ASCII grid path")
    parser.add_argument("--json", action="store_true", help="print JSON only")
    args = parser.parse_args()
    try:
        report = read_grid(args.asc)
        report["ok"] = report["values_read"] >= report["values_expected"]
    except Exception as error:
        report = {"ok": False, "path": str(args.asc), "error": str(error)}

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

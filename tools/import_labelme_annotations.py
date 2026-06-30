#!/usr/bin/env python3
"""Convert LabelMe JSON annotations into a normalized shoe localization CSV."""

import argparse
import json
import math
import os
import re
from pathlib import Path

import pandas as pd

LABEL_RE = re.compile(r"Shoe\s*\(([-\d.]+),\s*([-\d.]+),\s*([-\d.]+)\)")


def parse_args():
    parser = argparse.ArgumentParser(description="Build shoe localization CSV from LabelMe JSON files")
    parser.add_argument("--labelme-dir", required=True, help="Folder containing LabelMe .json annotations")
    parser.add_argument("--output-csv", default="data/shoe_dataset.csv")
    parser.add_argument("--max-distance-mm", type=float, default=2000.0)
    parser.add_argument("--basename-only", action="store_true", help="Store only image basenames in the CSV")
    return parser.parse_args()


def main():
    args = parse_args()
    records = []
    labelme_dir = Path(args.labelme_dir)
    for path in sorted(labelme_dir.glob("*.json")):
        data = json.loads(path.read_text())
        image_path = data.get("imagePath", "")
        width = float(data.get("imageWidth", 1) or 1)
        for shape in data.get("shapes", []):
            match = LABEL_RE.match(shape.get("label", ""))
            if not match:
                continue
            x_offset = float(match.group(1))
            z_distance = float(match.group(2))
            angle_deg = float(match.group(3))
            angle_rad = math.radians(angle_deg)
            records.append({
                "image": os.path.basename(image_path) if args.basename_only else image_path.replace("\\", "/"),
                "x_offset": x_offset,
                "z_distance": z_distance,
                "angle": angle_deg,
                "x_offset_norm": x_offset / (width / 2.0),
                "z_distance_norm": z_distance / args.max_distance_mm,
                "angle_sin": round(math.sin(angle_rad), 4),
                "angle_cos": round(math.cos(angle_rad), 4),
            })
    out = Path(args.output_csv)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).to_csv(out, index=False)
    print(f"Saved {len(records)} rows to {out}")


if __name__ == "__main__":
    main()

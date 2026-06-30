#!/usr/bin/env python3
"""Create a contact sheet from sample dataset images for README/documentation."""

import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image-dir", default="data/sample_images/scene2")
    parser.add_argument("--output", default="images/dataset_sample_contact_sheet.jpg")
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()
    paths = sorted(Path(args.image_dir).glob("*.jpg"))[: args.limit]
    if not paths:
        raise SystemExit("No .jpg images found")
    font = ImageFont.load_default()
    thumbs = []
    for p in paths:
        im = Image.open(p).convert("RGB")
        im.thumbnail((220, 150))
        canvas = Image.new("RGB", (220, 170), "white")
        canvas.paste(im, ((220 - im.width) // 2, 5))
        ImageDraw.Draw(canvas).text((8, 152), p.name[:28], font=font, fill=(30, 41, 59))
        thumbs.append(canvas)
    sheet = Image.new("RGB", (4 * 220, ((len(thumbs) + 3) // 4) * 170), "white")
    for i, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((i % 4) * 220, (i // 4) * 170))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.output, quality=88, optimize=True)
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()

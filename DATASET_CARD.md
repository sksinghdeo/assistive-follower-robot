# Dataset Card — OAK-D Shoe Localization Dataset

## Purpose

Train and test a camera-based model for estimating shoe position, distance, and orientation from a robot-mounted OAK-D camera.

## Files included

- `data/shoe_dataset.csv` — 200 labeled rows
- `data/sample_dataset.csv` — subset tied to included sample images
- `data/sample_images/` — compressed visual examples from Scene 1 and Scene 2
- `data/metadata/` — source archive and sample image manifests

## Raw data summary

```json
[
  {
    "archive": "Scene1_data.zip",
    "file_count": 232,
    "image_count": 232,
    "uncompressed_bytes": 338158978,
    "compressed_bytes": 337409071
  },
  {
    "archive": "scene2-dataset.zip",
    "file_count": 232,
    "image_count": 232,
    "uncompressed_bytes": 494666251,
    "compressed_bytes": 494576429
  }
]
```

## Label columns

```text
image, x_offset, z_distance, angle, x_offset_norm, z_distance_norm, angle_sin, angle_cos
```

## Notes

Full raw Scene 1 and Scene 2 image archives are intentionally not committed to keep the GitHub repo usable. Store those archives externally or with Git LFS if full reproducibility is needed.

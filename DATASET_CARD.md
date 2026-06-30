# Dataset Card — OAK-D Shoe Localization Dataset

## Purpose

Train and test a camera-based model for estimating shoe position, distance, and orientation from a robot-mounted OAK-D camera.

## Files included

- `data/shoe_dataset.csv` — 200 labeled rows
- `data/sample_dataset.csv` — subset tied to included sample images
- `data/sample_images/` — compressed visual examples from Scene 1 and Scene 2
- `data/metadata/` — source archive and sample image manifests

## Label columns

```text
image, x_offset, z_distance, angle, x_offset_norm, z_distance_norm, angle_sin, angle_cos
```

## Raw data summary

| Archive | Raw image count | Notes |
|---|---:|---|
| Scene 1 | 232 | sample frames committed, raw archive not committed |
| Scene 2 | 232 | sample frames + label CSV committed, raw archive not committed |

## Known limitations

- The dataset is controlled and indoor.
- Lighting, flooring, shoes, camera height, clutter, and robot motion should be expanded before claiming broad deployment.
- The dataset is suitable for demonstrating a prototype perception pipeline, not for safety-rated assistive navigation.

## Large-file policy

Full raw Scene 1 and Scene 2 image archives are intentionally not committed to keep the GitHub repo usable. Store those archives externally or with Git LFS if full reproducibility is needed.

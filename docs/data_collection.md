# Data Collection

The image dataset was collected with an OAK-D camera mounted on the robot at a fixed height. The floor was mapped so image locations could be related to physical shoe positions and distances.

## Capture setup

| OAK-D field-of-view mapping | Physical collection grid |
|---|---|
| <img src="../images/oakd_field_of_view_mapping.png" alt="OAK-D field-of-view mapping"> | <img src="../images/data_collection_grid.png" alt="Mapped floor grid used for image collection"> |

## Dataset coverage

| Source | Included in repo | Raw archive image count |
|---|---:|---:|
| Scene 1 | representative sample frames | 232 |
| Scene 2 | representative sample frames + full label CSV | 232 |

The raw image archives are intentionally not committed in full because they are too large for a clean GitHub portfolio repo. The included sample images, label CSV, manifests, and source documents show the dataset structure.

## Pose and distance variation

| Pose diversity | Distance variation |
|---|---|
| <img src="../images/pose_diversity_dataset.png" alt="Shoe pose diversity examples"> | <img src="../images/distance_variation_labels.png" alt="Distance variation label examples"> |

## Label format

Labels encode target pose as:

```text
Shoe (x_offset, z_distance, angle)
```

The CSV representation stores normalized values for model training:

```text
image, x_offset, z_distance, angle, x_offset_norm, z_distance_norm, angle_sin, angle_cos
```

| Label convention | LabelMe annotation workflow |
|---|---|
| <img src="../images/shoe_labeling_convention.png" alt="Shoe x-offset, z-distance, and angle convention"> | <img src="../images/labelme_interface.png" alt="LabelMe annotation workflow"> |

## Sample frames

<p align="center">
  <img src="../images/dataset_sample_contact_sheet.jpg" width="850" alt="Contact sheet of representative dataset images">
</p>

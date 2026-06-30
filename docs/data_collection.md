# Data Collection

The image dataset was collected with an OAK-D camera mounted on the robot at a fixed height. The data collection procedure used mapped floor positions so image location could be related to physical target location.

## Dataset coverage

| Source | Included in repo | Raw archive image count |
|---|---:|---:|
| Scene 1 | sample frames | 232 |
| Scene 2 | sample frames + label CSV | 232 |

The raw image archives are intentionally not committed in full because they are too large for a clean GitHub portfolio repo. The included sample images and contact sheet show the dataset structure.

![OAK-D field-of-view mapping](../images/oakd_field_of_view_mapping.png)

![Dataset sample contact sheet](../images/dataset_sample_contact_sheet.jpg)

## Label format

Labels encode target pose as:

```text
Shoe (x_offset, z_distance, angle)
```

The CSV representation stores normalized values for model training:

```text
image, x_offset, z_distance, angle, x_offset_norm, z_distance_norm, angle_sin, angle_cos
```

![Shoe labeling convention](../images/shoe_labeling_convention.png)

![LabelMe interface](../images/labelme_interface.png)

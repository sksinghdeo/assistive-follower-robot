# Model Weights

This folder contains the trained shoe localization model used by the portfolio package.

Included file:

```text
shoe_model.pth  (42.7 MB)
```

The model follows the ResNet18-style regression setup used in `tools/train_shoe_regressor.py` and predicts:

```text
[x_offset_norm, z_distance_norm, sin(theta), cos(theta)]
```

If GitHub rejects the model upload in the browser, use Git LFS or leave the file out and keep this README as the model placement guide.

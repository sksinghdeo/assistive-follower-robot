# Model Card — Shoe Localization Regressor

## Intended use

Estimate the relative shoe/user position from OAK-D RGB camera frames for an assistive follower robot prototype.

## Architecture

- Backbone: ResNet18-style CNN
- Output vector: `[x_offset_norm, z_distance_norm, sin(theta), cos(theta)]`
- Model file: `models/shoe_model.pth`
- Model size: 42.7 MB

## Dataset

The provided label CSV contains 200 samples. Raw Scene 1 and Scene 2 images were uploaded during repo preparation; this repo includes compressed samples and a manifest rather than all raw images.

## Limitations

- The dataset appears controlled and indoor.
- Generalization to new lighting, flooring, footwear, camera height, and clutter should be validated before real assistive deployment.
- The model estimates a target cue for navigation and is not a safety-rated person-following perception system.

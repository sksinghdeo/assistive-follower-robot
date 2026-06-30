# Data

This repo includes a GitHub-friendly dataset subset and the label table used for the shoe localization workflow.

Included:

- `shoe_dataset.csv` — full CSV label table provided with the project (200 rows)
- `sample_dataset.csv` — rows that point to the sample images included in this repo
- `sample_images/scene1/` — compressed sample frames from Scene 1
- `sample_images/scene2/` — compressed sample frames from Scene 2
- `metadata/raw_archive_manifest.json` — summary of the raw dataset archives uploaded during repo preparation
- `metadata/sample_image_manifest.csv` — source mapping for the included sample frames

Not included directly in git:

- full raw `Scene1_data.zip` (232 images)
- full raw `scene2-dataset.zip` (232 images)

Those raw archives are better stored outside GitHub or with Git LFS because they are hundreds of MB.

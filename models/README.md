# Models

This folder is expected to contain the trained PyTorch model weights:

```text
shoe_model.pth
```

The model file is hosted externally because it exceeds GitHub browser upload limits.

Download it here:

[Download shoe_model.pth](https://drive.google.com/file/d/1b0rS5kiqUQPc6da0CqnZwli_7nzqFTKU/view?usp=drive_link)

After downloading, place it in this folder so the final path is:

```text
models/shoe_model.pth
```

The ROS 2 vision node and standalone OAK-D inference script expect the model at this location.

To regenerate the model from the labeled dataset:

```bash
python tools/train_shoe_regressor.py \
  --csv data/shoe_dataset.csv \
  --image-dir /path/to/full/scene2/images \
  --output-model models/shoe_model.pth \
  --epochs 100
```

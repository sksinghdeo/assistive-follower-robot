# Models

`shoe_model.pth` is the trained PyTorch model supplied with this portfolio repository.

If GitHub blocks upload because of file size, either:

1. use Git LFS for `*.pth`, or
2. remove `models/shoe_model.pth` from the repo and keep this folder with instructions.

The model can be regenerated with:

```bash
python tools/train_shoe_regressor.py \
  --csv data/shoe_dataset.csv \
  --image-dir /path/to/full/scene2/images \
  --output-model models/shoe_model.pth \
  --epochs 100
```

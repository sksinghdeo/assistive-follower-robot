#!/usr/bin/env python3
"""Train a ResNet18-style shoe localization regressor.

Outputs four normalized regression values:
    [x_offset_norm, z_distance_norm, angle_sin, angle_cos]
"""

import argparse
from pathlib import Path

import pandas as pd
from PIL import Image
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import transforms
from torchvision.models import resnet18, ResNet18_Weights


class ShoeDataset(Dataset):
    def __init__(self, csv_file, image_dir, transform=None):
        self.data = pd.read_csv(csv_file)
        self.image_dir = Path(image_dir)
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]
        image_path = self.image_dir / str(row["image"])
        image = Image.open(image_path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        target = torch.tensor([
            row["x_offset_norm"],
            row["z_distance_norm"],
            row["angle_sin"],
            row["angle_cos"],
        ], dtype=torch.float32)
        return image, target


class ShoeRegressor(nn.Module):
    def __init__(self):
        super().__init__()
        self.backbone = resnet18(weights=ResNet18_Weights.DEFAULT)
        self.backbone.fc = nn.Linear(self.backbone.fc.in_features, 4)

    def forward(self, x):
        return self.backbone(x)


def parse_args():
    parser = argparse.ArgumentParser(description="Train shoe localization model")
    parser.add_argument("--csv", required=True, help="CSV generated from LabelMe annotations")
    parser.add_argument("--image-dir", required=True, help="Folder containing training images")
    parser.add_argument("--output-model", default="models/shoe_model.pth", help="Output model path")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--val-split", type=float, default=0.2)
    return parser.parse_args()


def main():
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ColorJitter(brightness=0.3, contrast=0.3),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    dataset = ShoeDataset(args.csv, args.image_dir, transform=transform)
    val_size = max(1, int(args.val_split * len(dataset)))
    train_size = len(dataset) - val_size
    train_data, val_data = random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_data, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_data, batch_size=args.batch_size)

    model = ShoeRegressor().to(device)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)

    for epoch in range(args.epochs):
        model.train()
        train_loss = 0.0
        for images, targets in train_loader:
            images, targets = images.to(device), targets.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for images, targets in val_loader:
                images, targets = images.to(device), targets.to(device)
                outputs = model(images)
                val_loss += criterion(outputs, targets).item()

        print(
            f"Epoch {epoch + 1}/{args.epochs} | "
            f"train={train_loss / max(len(train_loader), 1):.4f} | "
            f"val={val_loss / max(len(val_loader), 1):.4f}"
        )

    output_model = Path(args.output_model)
    output_model.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), output_model)
    print(f"Saved model to {output_model}")


if __name__ == "__main__":
    main()

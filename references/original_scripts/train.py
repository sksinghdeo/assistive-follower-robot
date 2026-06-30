import os
import pandas as pd
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import transforms
import torch.nn as nn
import torch.optim as optim
from torchvision.models import resnet18

# --- Custom Dataset ---
class ShoeDataset(Dataset):
    def __init__(self, csv_file, image_dir, transform=None):
        self.data = pd.read_csv(csv_file)
        self.image_dir = image_dir
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]
        image_path = os.path.join(self.image_dir, row['image'])
        image = Image.open(image_path).convert("RGB")
        if self.transform:
            image = self.transform(image)

        targets = torch.tensor([
            row['x_offset_norm'],
            row['z_distance_norm'],
            row['angle_sin'],
            row['angle_cos']
        ], dtype=torch.float32)

        return image, targets

# --- Model ---
class ShoeRegressor(nn.Module):
    def __init__(self):
        super(ShoeRegressor, self).__init__()
        self.backbone = resnet18(pretrained=True)
        self.backbone.fc = nn.Linear(self.backbone.fc.in_features, 4)  # 4 regression outputs

    def forward(self, x):
        return self.backbone(x)

# --- Training Function ---
def train():
    # Hyperparameters
    BATCH_SIZE = 8
    EPOCHS = 20
    LR = 1e-4
    VAL_SPLIT = 0.2
    CSV_FILE = "shoe_dataset.csv"
    IMAGE_DIR = "C:/Users/Owner/Pictures/Screenshots/Scene2/images"

    # Transforms
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(20),
        transforms.ColorJitter(brightness=0.3, contrast=0.3),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])

    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])

    # Load dataset
    full_dataset = ShoeDataset(CSV_FILE, IMAGE_DIR, transform=None)
    val_size = int(VAL_SPLIT * len(full_dataset))
    train_size = len(full_dataset) - val_size
    train_data, val_data = random_split(full_dataset, [train_size, val_size])

    # Apply transforms to splits
    train_data.dataset.transform = train_transform
    val_data.dataset.transform = val_transform

    train_loader = DataLoader(train_data, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_data, batch_size=BATCH_SIZE)

    # Model, loss, optimizer
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ShoeRegressor().to(device)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=LR)

    # Training loop
    for epoch in range(EPOCHS):
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

        # Validation
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for images, targets in val_loader:
                images, targets = images.to(device), targets.to(device)
                outputs = model(images)
                loss = criterion(outputs, targets)
                val_loss += loss.item()

        print(f"Epoch {epoch+1}/{EPOCHS}, Train Loss: {train_loss/len(train_loader):.4f}, "
              f"Val Loss: {val_loss/len(val_loader):.4f}")

    # Save model
    torch.save(model.state_dict(), "shoe_model.pth")
    print("Training complete. Model saved as shoe_model.pth")

if __name__ == "__main__":
    train()

import os
import json
import pandas as pd
import re
import math


labelme_dir = "C:/Users/Owner/Pictures/Screenshots/Scene2/Jason_files"
output_csv = "shoe_dataset.csv"

records = []

for filename in os.listdir(labelme_dir):
    if filename.endswith(".json"):
        filepath = os.path.join(labelme_dir, filename)
        with open(filepath, "r") as f:
            data = json.load(f)

        image_path = data.get("imagePath", "")
        width = data.get("imageWidth", 1)  # fallback to avoid division by 0
        height = data.get("imageHeight", 1)

        for shape in data["shapes"]:
            label = shape["label"]
            # Extract (x_offset, z_distance, angle) from label string
            match = re.match(r"Shoe \(([-\d]+),([-\d]+),([-\d]+)\)", label)
            if match:
                x_offset = int(match.group(1))        # mm from screen center
                z_distance = int(match.group(2))      # mm from camera
                angle_deg = int(match.group(3))       # degrees

                # Normalize x_offset (optional: assuming image center is at width/2)
                x_offset_norm = x_offset / (width / 2)  # now -1 to 1 if within screen
                z_distance_norm = z_distance / 2000.0   # assuming 2m max range
                angle_rad = angle_deg * 3.14159 / 180.0
                angle_sin = round(math.sin(angle_rad), 4)
                angle_cos = round(math.cos(angle_rad), 4)

                records.append({
                    "image": image_path.replace("\\", "/"),  # normalize path
                    "x_offset": x_offset,
                    "z_distance": z_distance,
                    "angle": angle_deg,
                    "x_offset_norm": x_offset_norm,
                    "z_distance_norm": z_distance_norm,
                    "angle_sin": angle_sin,
                    "angle_cos": angle_cos
                })

df = pd.DataFrame(records)
df.to_csv(output_csv, index=False)
print(f"Saved: {output_csv}")

import torch
from torchvision import transforms
from PIL import Image
import numpy as np
import cv2
import depthai as dai
import torchvision.models as models
import torch.nn as nn

# Set torch device
torch_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Define the model and load weights
model = models.resnet18(weights=None)
model.fc = nn.Linear(model.fc.in_features, 4)

state_dict = torch.load("shoe_model.pth")
cleaned_state_dict = {k.replace("backbone.", ""): v for k, v in state_dict.items()}
model.load_state_dict(cleaned_state_dict)
model.to(torch_device)
model.eval()

# Image transform (same as training)
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])  # Standard ImageNet normalization
])

# Create DepthAI pipeline
pipeline = dai.Pipeline()

cam_rgb = pipeline.createColorCamera()
cam_rgb.setPreviewSize(640, 480)
cam_rgb.setInterleaved(False)
cam_rgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)  # Use CAM_A instead of deprecated RGB

xout_video = pipeline.createXLinkOut()
xout_video.setStreamName("video")
cam_rgb.preview.link(xout_video.input)

# Start pipeline
with dai.Device(pipeline) as depthai_device:
    video = depthai_device.getOutputQueue(name="video", maxSize=4, blocking=False)

    while True:
        in_frame = video.get()
        frame = in_frame.getCvFrame()

        # Preprocess frame
        input_tensor = transform(frame).unsqueeze(0).to(torch_device)

        # Predict
        with torch.no_grad():
            prediction = model(input_tensor).squeeze().cpu().numpy()

        # Unpack prediction
        x_offset_norm, z_distance_norm, sin_theta, cos_theta = prediction

        # Convert normalized to actual (adjust as needed)
        frame_width = frame.shape[1]
        x_offset = x_offset_norm * frame_width

        z_distance = z_distance_norm * 2000  # 0–2000 mm range

        angle_rad = np.arctan2(sin_theta, cos_theta)
        angle_deg = np.degrees(angle_rad) % 360

        # Display results
        cv2.putText(frame, f"X Offset: {x_offset:.1f} mm", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Z Dist: {z_distance:.1f} mm", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Angle: {angle_deg:.1f} deg", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow("Shoe Tracker", frame)
        if cv2.waitKey(1) == ord('q'):
            break

cv2.destroyAllWindows()

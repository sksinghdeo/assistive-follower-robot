#!/usr/bin/env python3
"""Run trained shoe localization model on live OAK-D frames outside ROS 2."""

import argparse
import math
from pathlib import Path

import cv2
import depthai as dai
import numpy as np
import torch
import torch.nn as nn
from torchvision import models, transforms


def parse_args():
    parser = argparse.ArgumentParser(description="Live OAK-D shoe localization inference")
    parser.add_argument("--model", default="models/shoe_model.pth", help="Path to trained .pth model")
    parser.add_argument("--max-distance-mm", type=float, default=2000.0)
    return parser.parse_args()


def load_model(model_path):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, 4)
    state_dict = torch.load(model_path, map_location=device)
    cleaned = {k.replace("backbone.", ""): v for k, v in state_dict.items()}
    model.load_state_dict(cleaned)
    model.to(device)
    model.eval()
    return model, device


def make_pipeline():
    pipeline = dai.Pipeline()
    cam_rgb = pipeline.createColorCamera()
    cam_rgb.setPreviewSize(640, 480)
    cam_rgb.setInterleaved(False)
    cam_rgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)
    xout_video = pipeline.createXLinkOut()
    xout_video.setStreamName("video")
    cam_rgb.preview.link(xout_video.input)
    return pipeline


def main():
    args = parse_args()
    model_path = Path(args.model)
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    model, device = load_model(model_path)
    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    pipeline = make_pipeline()
    with dai.Device(pipeline) as depthai_device:
        video = depthai_device.getOutputQueue(name="video", maxSize=4, blocking=False)
        while True:
            frame = video.get().getCvFrame()
            input_tensor = transform(frame).unsqueeze(0).to(device)
            with torch.no_grad():
                pred = model(input_tensor).squeeze().cpu().numpy()

            x_norm, z_norm, sin_theta, cos_theta = pred
            x_offset = float(x_norm * frame.shape[1])
            z_distance = float(z_norm * args.max_distance_mm)
            angle_rad = math.atan2(float(sin_theta), float(cos_theta))
            angle_deg = math.degrees(angle_rad) % 360

            cv2.putText(frame, f"X Offset: {x_offset:.1f} px", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Z Dist: {z_distance:.1f} mm", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Angle: {angle_deg:.1f} deg", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("Shoe Tracker", frame)
            if cv2.waitKey(1) == ord("q"):
                break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

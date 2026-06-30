#!/usr/bin/env python3
"""Camera/model node that publishes a target heading angle in degrees."""

import math
import os
from pathlib import Path

import cv2
import rclpy
from ament_index_python.packages import get_package_share_directory
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Float32

try:
    import torch
    import torch.nn as nn
    from torchvision import models, transforms
except Exception:  # runtime error is raised with a clear message if used without torch
    torch = None
    nn = None
    models = None
    transforms = None


class VisionAngleNode(Node):
    """Estimate target heading from camera frames using a trained image regressor."""

    def __init__(self) -> None:
        super().__init__("vision_angle")
        self.declare_parameter("image_topic", "/color/preview/image")
        self.declare_parameter("heading_topic", "/rpi_11/person_heading_deg")
        self.declare_parameter("model_path", "models/shoe_model.pth")
        self.declare_parameter("max_distance_mm", 2000.0)
        self.declare_parameter("publish_debug_image", False)

        self.bridge = CvBridge()
        self.model, self.device, self.transform = self.load_model()
        self.heading_pub = self.create_publisher(Float32, self.get_parameter("heading_topic").value, 10)
        self.image_sub = self.create_subscription(Image, self.get_parameter("image_topic").value, self.image_callback, 10)
        self.get_logger().info("VisionAngleNode ready")

    def resolve_model_path(self) -> Path:
        configured = str(self.get_parameter("model_path").value)
        path = Path(configured)
        if path.exists():
            return path
        share_dir = Path(get_package_share_directory("assistive_follower_robot"))
        candidate = share_dir / configured
        if candidate.exists():
            return candidate
        candidate = share_dir / "models" / Path(configured).name
        if candidate.exists():
            return candidate
        raise FileNotFoundError(f"Model not found. Tried '{configured}' and package share models folder.")

    def load_model(self):
        if torch is None:
            raise RuntimeError("PyTorch/torchvision are required for vision_angle. Install requirements.txt.")
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = models.resnet18(weights=None)
        model.fc = nn.Linear(model.fc.in_features, 4)
        model_path = self.resolve_model_path()
        state_dict = torch.load(model_path, map_location=device)
        cleaned = {k.replace("backbone.", ""): v for k, v in state_dict.items()}
        model.load_state_dict(cleaned)
        model.to(device)
        model.eval()
        transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])
        return model, device, transform

    def image_callback(self, msg: Image) -> None:
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            input_tensor = self.transform(frame).unsqueeze(0).to(self.device)
            with torch.no_grad():
                x_norm, z_norm, sin_theta, cos_theta = self.model(input_tensor).squeeze().cpu().numpy()

            # Use sin/cos for a stable angle target, then remap to signed heading for steering.
            angle_deg = math.degrees(math.atan2(float(sin_theta), float(cos_theta)))
            if angle_deg > 180.0:
                angle_deg -= 360.0

            msg_out = Float32()
            msg_out.data = float(angle_deg)
            self.heading_pub.publish(msg_out)
        except Exception as exc:
            self.get_logger().error(f"vision inference failed: {exc}")


def main(args=None) -> None:
    rclpy.init(args=args)
    node = VisionAngleNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""LiDAR follow-the-gap navigation guided by a vision/user heading estimate."""

import math
from typing import Tuple

import numpy as np
import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32


class GapFollower(Node):
    """Reactive obstacle avoidance and user-heading guided motion controller."""

    def __init__(self) -> None:
        super().__init__("gap_follower")
        self.declare_parameter("scan_topic", "/rpi_11/scan")
        self.declare_parameter("cmd_vel_topic", "/rpi_11/cmd_vel")
        self.declare_parameter("heading_topic", "/rpi_11/person_heading_deg")
        self.declare_parameter("field_of_view_deg", 80.0)
        self.declare_parameter("smoothing_window", 10)
        self.declare_parameter("range_threshold_m", 1.0)
        self.declare_parameter("max_range_m", 6.0)
        self.declare_parameter("bubble_radius", 10)
        self.declare_parameter("max_linear_speed", 0.50)
        self.declare_parameter("min_linear_speed", 0.10)
        self.declare_parameter("angular_gain", 1.0)
        self.declare_parameter("heading_weight", 0.65)
        self.declare_parameter("emergency_stop_distance_m", 0.35)

        self.user_heading_rad = 0.0
        self.have_heading = False

        self.scan_sub = self.create_subscription(
            LaserScan, self.get_parameter("scan_topic").value, self.scan_callback, 10
        )
        self.heading_sub = self.create_subscription(
            Float32, self.get_parameter("heading_topic").value, self.heading_callback, 10
        )
        self.cmd_pub = self.create_publisher(
            Twist, self.get_parameter("cmd_vel_topic").value, 10
        )
        self.get_logger().info("GapFollower ready")

    def heading_callback(self, msg: Float32) -> None:
        self.user_heading_rad = math.radians(float(msg.data))
        self.have_heading = True

    def scan_callback(self, msg: LaserScan) -> None:
        ranges, angles = self.preprocess_scan(msg)
        if ranges.size == 0:
            self.publish_stop("empty scan after preprocessing")
            return

        valid = ranges[ranges > 0.0]
        if valid.size == 0:
            self.publish_stop("no valid LiDAR ranges")
            return

        nearest = float(np.min(valid))
        if nearest < float(self.get_parameter("emergency_stop_distance_m").value):
            self.publish_stop(f"emergency stop: nearest obstacle {nearest:.2f} m")
            return

        self.apply_obstacle_bubble(ranges)
        start, end = self.find_max_gap(ranges)
        if end <= start:
            self.publish_stop("no navigable gap")
            return

        best_idx = self.find_best_point(start, end, ranges, angles)
        steer_angle = float(angles[best_idx])
        self.cmd_pub.publish(self.compute_cmd(steer_angle, nearest))

    def preprocess_scan(self, msg: LaserScan) -> Tuple[np.ndarray, np.ndarray]:
        ranges = np.array(msg.ranges, dtype=np.float32)
        ranges[np.isnan(ranges) | np.isinf(ranges)] = 0.0
        ranges[ranges < msg.range_min] = 0.0
        max_range = float(self.get_parameter("max_range_m").value)
        ranges[(ranges > msg.range_max) | (ranges > max_range)] = max_range

        window = max(1, int(self.get_parameter("smoothing_window").value))
        if window > 1 and len(ranges) >= window:
            kernel = np.ones(window, dtype=np.float32) / window
            ranges = np.convolve(ranges, kernel, mode="same")

        angles = msg.angle_min + np.arange(len(ranges), dtype=np.float32) * msg.angle_increment
        fov = math.radians(float(self.get_parameter("field_of_view_deg").value))
        mask = (angles >= -fov) & (angles <= fov)
        return ranges[mask], angles[mask]

    def apply_obstacle_bubble(self, ranges: np.ndarray) -> None:
        if ranges.size == 0:
            return
        closest_idx = int(np.argmin(np.where(ranges > 0.0, ranges, np.inf)))
        radius = int(self.get_parameter("bubble_radius").value)
        ranges[max(0, closest_idx - radius):min(len(ranges), closest_idx + radius + 1)] = 0.0

    def find_max_gap(self, ranges: np.ndarray) -> Tuple[int, int]:
        threshold = float(self.get_parameter("range_threshold_m").value)
        free = ranges > threshold
        best_start = best_end = 0
        current_start = None
        for i, is_free in enumerate(free):
            if is_free and current_start is None:
                current_start = i
            if (not is_free or i == len(free) - 1) and current_start is not None:
                current_end = i if is_free else i - 1
                if current_end - current_start > best_end - best_start:
                    best_start, best_end = current_start, current_end
                current_start = None
        return best_start, best_end

    def find_best_point(self, start: int, end: int, ranges: np.ndarray, angles: np.ndarray) -> int:
        gap_indices = np.arange(start, end + 1)
        gap_ranges = ranges[gap_indices]
        gap_angles = angles[gap_indices]
        clearance_score = gap_ranges / max(float(np.max(gap_ranges)), 1e-6)
        heading_weight = float(self.get_parameter("heading_weight").value) if self.have_heading else 0.0
        heading_error = np.abs(gap_angles - self.user_heading_rad)
        heading_score = 1.0 - np.clip(heading_error / math.radians(180.0), 0.0, 1.0)
        score = (1.0 - heading_weight) * clearance_score + heading_weight * heading_score
        return int(gap_indices[int(np.argmax(score))])

    def compute_cmd(self, steer_angle: float, nearest_obstacle: float) -> Twist:
        max_speed = float(self.get_parameter("max_linear_speed").value)
        min_speed = float(self.get_parameter("min_linear_speed").value)
        angular_gain = float(self.get_parameter("angular_gain").value)
        steering_penalty = min(abs(steer_angle) / math.radians(80.0), 1.0)
        obstacle_penalty = max(0.0, min((nearest_obstacle - 0.35) / 2.0, 1.0))
        speed = min_speed + (max_speed - min_speed) * (1.0 - steering_penalty) * obstacle_penalty
        cmd = Twist()
        cmd.linear.x = float(max(min_speed, min(max_speed, speed)))
        cmd.angular.z = float(-angular_gain * steer_angle)
        return cmd

    def publish_stop(self, reason: str) -> None:
        self.get_logger().warn(reason)
        self.cmd_pub.publish(Twist())


def main(args=None) -> None:
    rclpy.init(args=args)
    node = GapFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

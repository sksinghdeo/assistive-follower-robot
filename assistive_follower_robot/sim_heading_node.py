#!/usr/bin/env python3
"""Small test node that publishes a fake heading angle for navigation testing."""

import math
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


class SimHeadingNode(Node):
    def __init__(self) -> None:
        super().__init__("sim_heading")
        self.declare_parameter("heading_topic", "/rpi_11/person_heading_deg")
        self.declare_parameter("publish_rate_hz", 5.0)
        self.declare_parameter("amplitude_deg", 20.0)
        self.declare_parameter("period_s", 8.0)
        self.publisher = self.create_publisher(Float32, self.get_parameter("heading_topic").value, 10)
        self.start_time = time.time()
        rate = float(self.get_parameter("publish_rate_hz").value)
        self.timer = self.create_timer(1.0 / max(rate, 0.1), self.publish_heading)

    def publish_heading(self) -> None:
        amplitude = float(self.get_parameter("amplitude_deg").value)
        period = float(self.get_parameter("period_s").value)
        elapsed = time.time() - self.start_time
        msg = Float32()
        msg.data = float(amplitude * math.sin(2.0 * math.pi * elapsed / max(period, 0.1)))
        self.publisher.publish(msg)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = SimHeadingNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

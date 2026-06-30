from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    package_name = "assistive_follower_robot"
    package_share = get_package_share_directory(package_name)
    params_file = os.path.join(package_share, "config", "params.yaml")

    use_vision = LaunchConfiguration("use_vision")
    use_sim_heading = LaunchConfiguration("use_sim_heading")

    return LaunchDescription([
        DeclareLaunchArgument("use_vision", default_value="true", description="Launch OAK-D/model heading node."),
        DeclareLaunchArgument("use_sim_heading", default_value="false", description="Launch fake heading publisher for testing."),
        Node(package=package_name, executable="gap_follower", name="gap_follower", output="screen", parameters=[params_file]),
        Node(package=package_name, executable="vision_angle", name="vision_angle", output="screen", parameters=[params_file], condition=IfCondition(use_vision)),
        Node(package=package_name, executable="sim_heading", name="sim_heading", output="screen", parameters=[params_file], condition=IfCondition(use_sim_heading)),
    ])

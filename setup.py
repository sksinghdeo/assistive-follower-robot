from glob import glob
import os
from setuptools import find_packages, setup

package_name = "assistive_follower_robot"

setup(
    name=package_name,
    version="1.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
        (os.path.join("share", package_name, "models"), glob("models/*.pth")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Shashank Singh Deo",
    maintainer_email="ssinghde@asu.edu",
    description="ROS 2 assistive follower robot using OAK-D vision, shoe localization, and LiDAR gap navigation.",
    license="NOASSERTION",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "gap_follower = assistive_follower_robot.gap_follower_node:main",
            "vision_angle = assistive_follower_robot.vision_angle_node:main",
            "sim_heading = assistive_follower_robot.sim_heading_node:main",
        ],
    },
)

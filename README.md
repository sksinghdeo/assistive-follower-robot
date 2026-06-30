<div align="center">

# Assistive Follower Robot

### ROS 2 mobile robot follower using OAK-D vision, learned shoe localization, and LiDAR gap navigation

Robotics · ROS 2 · TurtleBot4 · OAK-D · LiDAR · PyTorch · Computer Vision · Assistive Robotics

</div>

---

## Overview

This repository is a polished portfolio version of an assistive follower robot project. The system combines a robot-mounted **OAK-D camera**, a **ResNet18-style shoe localization model**, **LiDAR follow-the-gap navigation**, and **ROS 2 topic integration** to move a TurtleBot-style robot toward a user cue while avoiding obstacles.

> Hardware-dependent prototype: the navigation node can be tested with simulated heading input, but full functionality requires a robot, LiDAR scan topic, camera image topic, and trained model weights.

---

## System at a Glance

<p align="center">
  <img src="images/hardware_system_layout.png" width="850" alt="TurtleBot, ROS 2 workstation, Raspberry Pi, camera, LiDAR, and shoe target layout">
</p>

<p align="center">
  <img src="images/system_architecture.svg" width="900" alt="Assistive follower robot system architecture">
</p>

The robot uses camera input to estimate the user's relative heading, LiDAR to identify safe free-space gaps, and a control node to publish velocity commands.

---

## What This Project Shows

| Area | Evidence |
|---|---|
| ROS 2 integration | Separate perception, heading, and navigation nodes connected through clear topics |
| Robotics navigation | LiDAR preprocessing, obstacle bubble masking, free-space gap selection, and velocity control |
| Computer vision | OAK-D image stream, trained ResNet18-style inference, and target angle estimation |
| ML workflow | LabelMe annotation, normalized regression labels, PyTorch training, model card, and dataset card |
| Hardware awareness | TurtleBot/OAK-D/LiDAR deployment assumptions, launch/config files, and safety notes |
| Portfolio quality | Clean README, docs, diagrams, sample images, model weights, and reproducible tooling |

---

## Dataset and Vision Model

The shoe localization pipeline predicts four regression outputs:

```text
[x_offset_norm, z_distance_norm, sin(theta), cos(theta)]
```

The included dataset material contains:

- `data/shoe_dataset.csv` — 200 labeled rows
- `data/sample_images/` — compressed sample frames from Scene 1 and Scene 2
- `models/shoe_model.pth` — trained model file (42.7 MB)
- `tools/` — scripts for LabelMe import, training, and live OAK-D inference

<p align="center">
  <img src="images/shoe_labeling_convention.png" width="650" alt="Shoe labeling convention for x offset, distance, and orientation">
</p>

<p align="center">
  <img src="images/dataset_sample_contact_sheet.jpg" width="850" alt="Sample OAK-D dataset frames">
</p>

<p align="center">
  <img src="images/vision_prediction_output.png" width="750" alt="Live shoe localization prediction output">
</p>

---

## Repository Structure

```text
assistive-follower-robot/
├── README.md
├── package.xml
├── setup.py
├── setup.cfg
├── requirements.txt
├── MODEL_CARD.md
├── DATASET_CARD.md
├── config/
│   └── params.yaml
├── launch/
│   └── follower.launch.py
├── assistive_follower_robot/
│   ├── gap_follower_node.py
│   ├── vision_angle_node.py
│   └── sim_heading_node.py
├── tools/
│   ├── import_labelme_annotations.py
│   ├── train_shoe_regressor.py
│   ├── live_oakd_predict.py
│   └── make_sample_contact_sheet.py
├── models/
│   └── shoe_model.pth
├── data/
│   ├── shoe_dataset.csv
│   ├── sample_dataset.csv
│   ├── sample_images/
│   └── metadata/
├── images/
├── docs/
└── references/
```

---

## ROS 2 Nodes

| Node | Purpose | Subscribes | Publishes |
|---|---|---|---|
| `gap_follower` | Reactive LiDAR gap navigation guided by target heading | `/rpi_11/scan`, `/rpi_11/person_heading_deg` | `/rpi_11/cmd_vel` |
| `vision_angle` | Camera/model-based heading prediction | `/color/preview/image` | `/rpi_11/person_heading_deg` |
| `sim_heading` | Fake heading publisher for testing without camera/model | none | `/rpi_11/person_heading_deg` |

This cleaned package uses `std_msgs/Float32` for the perception-navigation interface so the topic contract is simple and explicit.

---

## Quick Start

### 1. Clone into a ROS 2 workspace

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone https://github.com/sksinghdeo/assistive-follower-robot.git
```

### 2. Install Python dependencies

```bash
cd ~/ros2_ws/src/assistive-follower-robot
pip install -r requirements.txt
```

### 3. Build the package

```bash
cd ~/ros2_ws
colcon build --packages-select assistive_follower_robot
source install/setup.bash
```

---

## Run Options

### Option A — Test navigation with simulated heading

Use this when you have LiDAR data but do not want to run the vision model yet.

```bash
ros2 launch assistive_follower_robot follower.launch.py use_sim_heading:=true use_vision:=false
```

### Option B — Run full follower stack

Use this when the robot camera, LiDAR, and model file are available.

```bash
ros2 launch assistive_follower_robot follower.launch.py use_sim_heading:=false use_vision:=true
```

### Option C — Run nodes separately

```bash
ros2 run assistive_follower_robot gap_follower
ros2 run assistive_follower_robot vision_angle
ros2 run assistive_follower_robot sim_heading
```

---

## Train / Rebuild the Shoe Model

### Build CSV from LabelMe JSON annotations

```bash
python tools/import_labelme_annotations.py   --labelme-dir /path/to/Jason_files   --output-csv data/shoe_dataset.csv   --basename-only
```

### Train the model

```bash
python tools/train_shoe_regressor.py   --csv data/shoe_dataset.csv   --image-dir /path/to/full/scene2/images   --output-model models/shoe_model.pth   --epochs 100
```

### Run live OAK-D inference outside ROS 2

```bash
python tools/live_oakd_predict.py --model models/shoe_model.pth
```

---

## Documentation

- [System overview](docs/system_overview.md)
- [Hardware](docs/hardware.md)
- [Data collection](docs/data_collection.md)
- [Vision model](docs/vision_model.md)
- [ROS 2 nodes](docs/ros2_nodes.md)
- [Testing and validation](docs/testing.md)
- [Portfolio scope](docs/portfolio_scope.md)
- [Model card](MODEL_CARD.md)
- [Dataset card](DATASET_CARD.md)

---

## Safety and Limitations

This is a prototype research/class project, not a certified assistive mobility product. Validate the robot at low speed in a controlled environment, verify `/cmd_vel` output before enabling motion, and keep emergency stop access available during testing.

Raw Scene 1 and Scene 2 archives are not committed in full because they are hundreds of MB. The repo includes representative sample frames, label CSVs, manifests, source documents, and the trained model file.

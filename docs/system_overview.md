# System Overview

The assistive follower robot combines perception, target heading estimation, and reactive navigation.

## High-level flow

<p align="center">
  <img src="../images/system_architecture.svg" width="900" alt="System architecture">
</p>

1. The OAK-D camera provides RGB image frames.
2. A PyTorch vision node estimates the user/shoe heading cue.
3. The heading is published as `std_msgs/Float32` on `/rpi_11/person_heading_deg`.
4. The LiDAR node processes `/rpi_11/scan` for navigable free-space gaps.
5. The gap follower combines safe free-space selection with target heading bias.
6. The controller publishes `/rpi_11/cmd_vel`.

## ROS 2 node graph

<p align="center">
  <img src="../images/node_graph.svg" width="850" alt="ROS 2 node graph">
</p>

## Why the interface was cleaned

The original team package mixed a vision topic published as a string with a navigation subscriber expecting a path-like message. This portfolio version uses a single explicit heading topic:

```text
/rpi_11/person_heading_deg   std_msgs/Float32
```

That makes the perception-navigation contract easier to test, document, and maintain.

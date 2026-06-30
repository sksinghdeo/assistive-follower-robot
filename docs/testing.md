# Testing and Validation

## Recommended checks

1. Confirm LiDAR publishes on `/rpi_11/scan`.
2. Confirm camera publishes on `/color/preview/image`.
3. Run `sim_heading` first to test navigation without the vision model.
4. Verify `/rpi_11/cmd_vel` output is safe before enabling motor motion.
5. Run the full stack with `vision_angle` after confirming the model path and camera topic.

## Commands

```bash
ros2 topic echo /rpi_11/scan
ros2 topic echo /rpi_11/person_heading_deg
ros2 topic echo /rpi_11/cmd_vel
```

## Safety note

This is a prototype follower stack. Use a low-speed test environment, keep emergency stop access available, and verify command output before running near people.

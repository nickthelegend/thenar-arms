# R3 follower / L1 leader joint conventions

This document records the existing firmware. No firmware source or calibration was changed. Source evidence: `thenar/model.h`, `thenar/calibration.h`, `thenar/thenar.ino`, and the current published assembly manifest.

| Logical joint | Index / PCA9685 channel / TCA9548A channel | Parent → child | Command limits (deg) | Home (deg) | Neutral (µs) | Default sign |
|---|---:|---|---:|---:|---:|---:|
| shoulder_pan | 0 | base_link → shoulder_link | −85 … +85 | 0 | 1500 | +1 |
| shoulder_lift | 1 | shoulder_link → upper_arm_link | −80 … +80 | −25 | 1500 | +1 |
| elbow_flex | 2 | upper_arm_link → lower_arm_link | −80 … +80 | +35 | 1500 | +1 |
| wrist_flex | 3 | lower_arm_link → wrist_link | −80 … +80 | 0 | 1500 | +1 |
| wrist_roll | 4 | wrist_link → gripper_link | −85 … +85 | 0 | 1500 | +1 |
| gripper | 5 | gripper_link → moving_jaw_so101_v1_link | 0 … +70 | +20 | 1500 | +1 |

Positive geometric angle is right-hand rotation about each joint datum's local +Z. These axes have different orientations in the global frame; +Z is not a global-axis instruction. Joint 5 rotates the moving jaw directly against the fixed gripper-body finger.

The follower uses `current[i]` / `goal[i]`, with `pulse = SERVO_ZERO_US[i] + q[i] * US_PER_DEGREE[i] * SERVO_SIGN[i]`. The stored default slope is 5.555556 µs/degree and default sign is +1 for all channels. Pulse guards are 1000–2000 µs for every channel. These are SOURCE VERIFIED software values; actual neutral indexing, positive physical servo rotation, pulse endpoints and mechanically safe travel are UNVERIFIED. The CAD convention cannot establish them. `FOLLOWER_CALIBRATED=false` remains unchanged.

Each axis is direct drive (1:1). The historical custom arm's 2:1 calibration does not apply. Servo control is on PCA9685 outputs 0–5, not six direct ESP32 servo GPIOs. Both controllers use ESP32 GPIO21 SDA / GPIO22 SCL. The follower driver is at I²C address 0x40; GPIO25 controls OE. The leader mux is at 0x70 and selects one of six AS5600 sensors at address 0x36.

The leader's `ZERO` command stores raw sensor readings at HOME, not at geometric q=0. Its conversion is `q[i] = model::home[i] + signs[i] * wrappedDegrees(raw[i], zeros[i])`. `wrappedDegrees` uses a 12-bit signed wrap and 360/4096 degrees/count. Sensor signs default to +1 and can be calibrated through `SIGN i +/-1`; neither sensor signs nor stored hardware zero readings are supplied in the project.

The source's preview/command limits do not prove independent or combined collision-free travel. The follower's sampled table intersections and the leader's folded collisions remain documented limitations. Physical min/max values are UNVERIFIED and must not be inferred from the 180-degree servo label.

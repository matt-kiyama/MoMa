# Arm Controller Guide

This guide explains how `controller_refactor` works internally and how to tune it safely.

## 1) Scope

This document covers:

- Controller data flow and execution sequence
- Control equations used for linear X and angular Z
- Runtime parameter update safety lock
- Tuning variable behavior and recommended tuning process

Primary implementation file:

- `tm_custom/src/arm_controller/arm_controller/controller_node_refactor.py`

## 2) Runtime Architecture

### Node

- Executable: `controller_refactor`
- Node name: `arm_service`

### Subscriptions

- `feedback_states` (`tm_msgs/msg/FeedbackState`)
  - Used for tool force (`tcp_force`) and tool pose (`tool_pose`)
- `sta_response` (`tm_msgs/msg/StaResponse`)
  - Status message handling (queue-tag related)
- `ld250_pose` (`nav_msgs/msg/Odometry`)
  - Used to determine whether base is stopped for safe parameter updates

### Publisher

- `/platform/velocity_command` (`geometry_msgs/msg/Twist`)
  - Output command to the mobile base controller

### Runtime Tuning GUI

- Executable: `stiff_tuner_gui`
- Node name: `stiff_param_tuner_gui`
- Writes `stiff_arm.*` parameters to `arm_service`

## 3) Controller Execution Flow

Each time a `feedback_states` message arrives, `_stiff_arm_control()` runs.

1. Compute control period `dt`
- `dt = now - prev_time`
- fallback to `0.01` seconds if `dt <= 0` or `dt > 0.1`

2. Clamp raw force input
- `tcp_force[0]` and `tcp_force[1]` are clamped using:
  - `force_min`
  - `force_max`

3. Low-pass filter force
- X channel: `alpha_fx = 0.2`
- Y channel: `alpha_fy = 0.12`
- Smoothed values become `tcp_fx` and `tcp_fy`

4. Apply deadband
- X deadband: `|tcp_fx| < 0.4` -> `tcp_fx = 0`
- Y deadband: `|tcp_fy| < 0.6` -> `tcp_fy = 0`

5. Apply axis blending
- Fixed blending constants:
  - `blend_strength_x = 0.2`
  - `blend_strength_z = 1.4`
- When X is dominant, Z is suppressed more strongly.

6. Compute linear X command path
- Desired velocity:
  - `vx_des = gain_linear_x * tcp_fx - damping_linear_x * prev_vx`
- Rate limit mode:
  - Accel: `acc_limit_x`
  - Decel: `dec_limit_x`
  - Reversal: `acc_limit_x * reversal_limit`
- Apply rate limiting and clamp to:
  - `vel_min_x <= vx <= vel_max_x`
- Apply tiny-output deadband:
  - `|vx| < 0.0005` -> `vx = 0`

7. Compute angular Z command path
- Desired velocity:
  - `wz_des = gain_angular_z * tcp_fy - damping_angular_z * prev_wz`
- Rate limit mode:
  - Accel: `acc_limit_z`
  - Decel: `acc_limit_z * 0.35` (fixed)
  - Reversal: `acc_limit_z * 1.5` (fixed)
- Apply rate limiting and clamp to:
  - `vel_min_z <= wz <= vel_max_z`
- Apply tiny-output deadband:
  - `|wz| < 0.0005` -> `wz = 0`

8. Publish and update state
- Publish:
  - `Twist.linear.x = vx`
  - `Twist.angular.z = wz`
- Save state:
  - `prev_vx = vx`
  - `prev_wz = wz`

## 4) Runtime Parameter Safety Lock

All tunables are exposed as ROS parameters under `stiff_arm.*`.

The controller rejects tuning updates unless the base is stopped.

Stop criteria:

- `|linear.x| <= 0.01`
- `|linear.y| <= 0.01`
- `|angular.z| <= 0.02`
- Conditions above must hold continuously for at least `0.25` seconds

If not stopped, parameter writes fail with:

- `Base must be stopped for at least 0.25s before tuning parameters.`

## 5) Tuning Variables (What They Control)

### Force clamps

- `force_max`, `force_min`
- Limit measured force before control law.
- Use these to bound aggressiveness and avoid extreme command requests.

### Linear X responsiveness and stability

- `gain_linear_x`
  - Higher: more responsive X motion
  - Lower: less responsive X motion
- `damping_linear_x`
  - Higher: stronger resistance, reduced overshoot
  - Lower: more glide, more potential oscillation

### Linear X motion shaping

- `acc_limit_x`
  - How quickly X velocity grows
- `dec_limit_x`
  - How quickly X velocity is reduced
- `reversal_limit`
  - Reversal multiplier on `acc_limit_x` when changing X direction

### Linear X speed envelope

- `vel_max_x`, `vel_min_x`
- Absolute output limits for X speed

### Angular Z responsiveness and stability

- `gain_angular_z`
  - Force-Y to yaw-rate sensitivity
- `damping_angular_z`
  - Resistance on yaw-rate

### Angular Z motion shaping and envelope

- `acc_limit_z`
  - Primary yaw rate-change limit
- `vel_max_z`, `vel_min_z`
  - Absolute output limits for yaw rate

## 6) Validation Rules For Tunables

Updates are rejected unless:

- `force_min < force_max`
- `vel_min_x < vel_max_x`
- `vel_min_z < vel_max_z`
- `acc_limit_x > 0`
- `dec_limit_x > 0`
- `reversal_limit > 0`
- `acc_limit_z > 0`
- `gain_linear_x >= 0`
- `gain_angular_z >= 0`
- `damping_linear_x >= 0`
- `damping_angular_z >= 0`

## 7) Recommended Tuning Procedure

1. Set safety limits first
- `vel_max_x`, `vel_min_x`, `vel_max_z`, `vel_min_z`
- `force_max`, `force_min`

2. Tune sensitivity
- `gain_linear_x` first
- `gain_angular_z` second

3. Tune damping
- `damping_linear_x` first
- `damping_angular_z` second

4. Tune motion feel
- `acc_limit_x`
- `dec_limit_x`
- `reversal_limit`
- `acc_limit_z`

5. Re-test against real use case
- Small pushes
- Quick release
- Direction reversals
- Repeated start/stop behavior

## 8) Symptom -> Adjustment Cheat Sheet

- Too jumpy in X:
  - decrease `gain_linear_x`
  - increase `damping_linear_x`
  - decrease `acc_limit_x`

- X feels sluggish:
  - increase `gain_linear_x`
  - decrease `damping_linear_x`
  - increase `acc_limit_x`

- X overshoots after release:
  - increase `damping_linear_x`
  - increase `dec_limit_x` if stopping is too slow

- Reversal feels harsh:
  - decrease `reversal_limit`
  - decrease `acc_limit_x`

- Reversal feels delayed:
  - increase `reversal_limit`
  - increase `acc_limit_x` slightly

- Yaw turns too fast:
  - decrease `gain_angular_z`
  - increase `damping_angular_z`
  - lower `vel_max_z`

- Yaw turns too slow:
  - increase `gain_angular_z`
  - decrease `damping_angular_z`
  - raise `vel_max_z` cautiously

## 9) Run Commands

Build:

```bash
colcon build --packages-select arm_controller
source install/setup.bash
```

Launch controller + GUI:

```bash
ros2 launch arm_controller stiff_tuning.launch.py
```

Manual split:

```bash
ros2 run arm_controller controller_refactor
ros2 run arm_controller stiff_tuner_gui
```

## 10) Notes On Non-Tunable Internals

The following remain fixed in code:

- Force filter coefficients (`alpha_fx`, `alpha_fy`)
- Force deadbands (X and Y)
- Axis blending strengths
- Z decel and reversal multipliers (`0.35`, `1.5`)

If tuning reaches limits, these may be the next candidates to expose as parameters.

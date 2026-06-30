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
- `/platform/odometry` (`nav_msgs/msg/Odometry`)
  - Used to determine whether base is stopped for safe parameter updates
  - Subscribed with sensor-data/best-effort QoS to match the base publisher

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
- If raw force returns inside the deadband, or changes sign against the filtered force, the filtered value is reset to `0`. This prevents the filter tail from commanding continued motion after release.

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

- `|linear.x| <= 0.03` by default
- `|linear.y| <= 0.03` by default
- `|angular.z| <= 0.05` by default
- Conditions above must hold continuously for at least `0.25` seconds

The thresholds and hold time are ROS parameters:

- `stop_linear_x_threshold`
- `stop_linear_y_threshold`
- `stop_angular_z_threshold`
- `stop_hold_time_sec`

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

### Core math (used by all examples)

Linear X:

- `vx_des = gain_linear_x * tcp_fx - damping_linear_x * prev_vx`
- `vx_next = prev_vx + clip(vx_des - prev_vx, -rate_x * dt, rate_x * dt)`
- `vx_cmd = clip(vx_next, vel_min_x, vel_max_x)`

Where `rate_x` is:

- `acc_limit_x` during accel
- `dec_limit_x` during decel
- `acc_limit_x * reversal_limit` during reversal

Angular Z:

- `wz_des = gain_angular_z * tcp_fy - damping_angular_z * prev_wz`
- `wz_next = prev_wz + clip(wz_des - prev_wz, -rate_z * dt, rate_z * dt)`
- `wz_cmd = clip(wz_next, vel_min_z, vel_max_z)`

Where `rate_z` is:

- `acc_limit_z` during accel
- `acc_limit_z * 0.35` during decel
- `acc_limit_z * 1.5` during reversal

Below, examples use `dt = 0.02 s` (50 Hz).

### A) Too jumpy in X

What math shows:

- Per-cycle jump size is bounded by `acc_limit_x * dt`.
- With `acc_limit_x = 0.30`, jump is `0.006 m/s` each cycle.
- With `acc_limit_x = 1.20`, jump is `0.024 m/s` each cycle (4x sharper).

Action:

- Decrease `acc_limit_x` first for smoother onset.
- If still jumpy, decrease `gain_linear_x` and/or increase `damping_linear_x`.

### B) X feels sluggish

What math shows:

- If ramp is too small, response lags even when `vx_des` is large.
- Example: from `0` to `0.04 m/s` cap:
  - `acc_limit_x = 0.30` -> `0.04 / (0.30*0.02) = ~7 cycles` (~0.14 s)
  - `acc_limit_x = 0.10` -> `0.04 / (0.10*0.02) = ~20 cycles` (~0.40 s)

Action:

- Increase `acc_limit_x` for faster rise.
- For low-force response, increase `gain_linear_x` slightly.
- If response is sticky, decrease `damping_linear_x`.

### C) X overshoots after release

At force release, raw `tcp_force[0]` should return inside the `0.4 N` deadband. The controller resets the filtered X force to `0`, so:

- `vx_des = -damping_linear_x * prev_vx`

Example with `prev_vx = 0.03 m/s`:

- `damping_linear_x = 0.12` -> `vx_des = -0.0036`
- Decel step size with `dec_limit_x = 0.072`:
  - max change per cycle = `0.072*0.02 = 0.00144 m/s`
  - stop time from `0.03` is about `0.03 / 0.00144 = ~21 cycles` (~0.42 s)

Action:

- First confirm the release reset is happening in the CSV log: `raw_tcp_fx` should be inside the deadband, `tcp_fx` should become `0`, and `limit_type_x` should switch to `DECEL`.
- Increase `dec_limit_x` to shorten stop time.
- Increase `damping_linear_x` if coasting persists.
- If `raw_tcp_fx` remains outside the deadband after you let go, the issue is force bias/noise or contact still loading the tool, not the velocity deceleration limit.

### D) Reversal feels harsh vs delayed

In reversal, `rate_x = acc_limit_x * reversal_limit`.

Example with `acc_limit_x = 0.30`:

- `reversal_limit = 0.30` -> `rate_x = 0.09`, step = `0.0018 m/s/cycle`
- `reversal_limit = 1.50` -> `rate_x = 0.45`, step = `0.0090 m/s/cycle`

From `+0.03` to `-0.03 m/s` (total change `0.06`):

- at `0.0018` step -> ~33 cycles (~0.66 s) -> delayed feel
- at `0.0090` step -> ~7 cycles (~0.14 s) -> sharp/harsh feel

Action:

- Harsh reversal: lower `reversal_limit` or `acc_limit_x`.
- Delayed reversal: raise `reversal_limit` modestly.

### E) Yaw turns too fast

What math shows:

- Yaw is usually bounded by `vel_max_z` for moderate/large force.
- Example with `tcp_fy = 1.0`, `gain_angular_z = 1.1`, `prev_wz = 0`:
  - `wz_des = 1.1 rad/s` (much larger than default cap `0.05`)
  - output will quickly hit `vel_max_z`.

Action:

- Lower `vel_max_z` to limit top turn speed.
- Decrease `gain_angular_z` for softer sensitivity.
- Increase `damping_angular_z` to reduce turn carry-over after release.

### F) Yaw turns too slow

What math shows:

- Rise time depends on `acc_limit_z`.
- To reach `0.05 rad/s` from zero:
  - `acc_limit_z = 0.35` -> step `0.007`, ~8 cycles (~0.16 s)
  - `acc_limit_z = 0.10` -> step `0.002`, ~25 cycles (~0.50 s)

Action:

- Increase `acc_limit_z` for faster turn onset.
- Increase `gain_angular_z` if low-force turning is weak.
- Raise `vel_max_z` cautiously only if safe.

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

If idle odometry noise keeps the GUI in `MOVING`, pass matching thresholds to both nodes through launch:

```bash
ros2 launch arm_controller stiff_tuning.launch.py \
  stop_linear_x_threshold:=0.04 \
  stop_linear_y_threshold:=0.04 \
  stop_angular_z_threshold:=0.06
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

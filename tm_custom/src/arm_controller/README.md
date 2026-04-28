# Arm Controller: Live Stiff-Arm Tuning

This package now supports live tuning of stiff-arm controller gains/limits while the controller is running, with a safety lock that only allows parameter updates when the mobile base is stopped.

Additional docs:

- `CONTROLLER_GUIDE.md`: full controller internals and tuning playbook

## What Was Added

- Runtime ROS parameters for all stiff-arm tuning fields under `stiff_arm.*`.
- Safety gate for parameter updates:
  - Uses `/platform/odometry` (`nav_msgs/msg/Odometry`).
  - Subscribes with sensor-data/best-effort QoS to match the base odometry publisher.
  - Update accepted only if:
    - `|linear.x| <= 0.03` by default
    - `|linear.y| <= 0.03` by default
    - `|angular.z| <= 0.05` by default
    - conditions held continuously for at least `0.25 s`
  - These thresholds are configurable with `stop_linear_x_threshold`,
    `stop_linear_y_threshold`, `stop_angular_z_threshold`, and `stop_hold_time_sec`.
- New GUI node for live tuning:
  - executable: `stiff_tuner_gui`
  - node name: `stiff_param_tuner_gui`
- Runtime-only behavior: tuned values are not persisted and return to defaults after restart.

## Nodes And Topics

### `controller_refactor` (`arm_service`)

- Subscribes:
  - `feedback_states` (`tm_msgs/msg/FeedbackState`)
  - `sta_response` (`tm_msgs/msg/StaResponse`)
  - `/platform/odometry` (`nav_msgs/msg/Odometry`) for stop/moving detection
- Publishes:
  - `/platform/velocity_command` (`geometry_msgs/msg/Twist`)

### `stiff_tuner_gui` (`stiff_param_tuner_gui`)

- Reads/writes parameters on controller node `arm_service` (configurable).
- Subscribes to odometry (`/platform/odometry` by default, sensor-data/best-effort QoS)
  to show `STOPPED` / `MOVING` status.
- Shows the latest odometry velocities so a persistent `MOVING` state can be diagnosed.

## Tunable Parameters

All of these are ROS parameters under `stiff_arm.*`:

- `force_max`
- `force_min`
- `vel_max_z`
- `vel_min_z`
- `vel_max_x`
- `vel_min_x`
- `gain_linear_x`
- `gain_angular_z`
- `acc_limit_x`
- `dec_limit_x`
- `reversal_limit`
- `acc_limit_z`
- `damping_linear_x`
- `damping_angular_z`

## Detailed Tuning Guide

This section explains exactly how each variable affects the control output.

### 1) Control Law Reference

Linear X path:

- `tcp_fx` is clamped by `force_min/force_max`, filtered, and reset to `0` when raw X force returns inside the release deadband, then used in:
- `vx_des = gain_linear_x * tcp_fx - damping_linear_x * prev_vx`
- `vx` is rate-limited:
  - accel phase: `acc_limit_x`
  - decel phase: `dec_limit_x`
  - reversal phase: `acc_limit_x * reversal_limit`
- final `vx` is clamped to `vel_min_x/vel_max_x`

Angular Z path:

- `tcp_fy` is clamped by `force_min/force_max`, filtered, then used in:
- `wz_des = gain_angular_z * tcp_fy - damping_angular_z * prev_wz`
- `wz` is rate-limited using `acc_limit_z` (decel path is derived in code from it)
- final `wz` is clamped to `vel_min_z/vel_max_z`

### 2) Parameter-By-Parameter Guidance

| Parameter | What it does | If too high | If too low | Tuning tip |
|---|---|---|---|---|
| `force_max` | Upper force clamp before control law (N). | Feels overly aggressive on hard pushes. | Saturates early, won’t respond proportionally to stronger push. | Start conservative; increase only if you see frequent clamp saturation. |
| `force_min` | Lower force clamp before control law (N). | Same risk as above in negative direction. | Negative-direction commands saturate too early. | Keep roughly symmetric with `force_max` unless asymmetry is intentional. |
| `gain_linear_x` | Converts force-X to desired linear speed. | Twitchy, oversensitive fore/aft motion. | Sluggish base response in X. | Increase in small steps (~5-15%) until responsiveness is acceptable. |
| `damping_linear_x` | Opposes current X speed to reduce overshoot. | Feels heavy/sticky; hard to keep moving. | Oscillation or overshoot in X. | Raise this after gain if X feels “bouncy.” |
| `acc_limit_x` | Max ramp rate for increasing X speed (m/s²). | Jerky/abrupt acceleration. | Slow to pick up speed from rest. | Tune for comfort and traction limits of your base. |
| `dec_limit_x` | Ramp rate when reducing X speed magnitude (m/s²). | Harsh braking feel, sudden slowdown. | Long coasting/stopping distance. | Lower for smoother stop; raise for tighter control. |
| `reversal_limit` | Multiplier on `acc_limit_x` during X direction reversal. | Snappy reversal, possible jerk/chatter. | Hesitant reversal with lag crossing through zero. | Keep near current value; increase only if reversals feel delayed. |
| `vel_max_x` | Positive X speed cap (m/s). | Base can move too fast for safe hand-guiding. | Tops out too early. | Set from safety/ops speed policy first, then tune gains. |
| `vel_min_x` | Negative X speed cap (m/s). | Too fast in reverse direction. | Reverse motion feels artificially weak. | Match magnitude of `vel_max_x` unless asymmetric behavior is needed. |
| `gain_angular_z` | Converts force-Y to desired yaw rate. | Over-rotates easily; hard to make fine turns. | Requires large force to rotate. | Increase gradually after X tuning is stable. |
| `damping_angular_z` | Opposes current yaw rate to smooth turns. | Feels resistant to turning. | Yaw overshoot or oscillatory turn response. | Raise if yaw keeps “coasting” after force release. |
| `acc_limit_z` | Max ramp rate for yaw speed changes (rad/s²). | Sharp rotational onset. | Slow turn initiation. | Tune for comfort and anti-slip behavior during turning. |
| `vel_max_z` | Positive yaw-rate cap (rad/s). | Rotation may feel unsafe/too fast. | Cannot reach desired turning speed. | Set by safety first, then raise only as needed. |
| `vel_min_z` | Negative yaw-rate cap (rad/s). | Too fast in opposite rotation direction. | Opposite direction feels weak. | Usually keep symmetric with `vel_max_z`. |

### 3) Recommended Tuning Order

1. Set safety envelopes first:
   - `vel_max_x`, `vel_min_x`, `vel_max_z`, `vel_min_z`
   - `force_max`, `force_min`
2. Tune responsiveness:
   - `gain_linear_x`, then `gain_angular_z`
3. Add damping for stability:
   - `damping_linear_x`, then `damping_angular_z`
4. Shape motion feel:
   - `acc_limit_x`, `dec_limit_x`, `reversal_limit`, `acc_limit_z`
5. Re-check caps:
   - confirm behavior never relies on constant saturation at velocity limits.

### 4) Practical Test Routine

Use the same short test sequence after each change:

1. Apply a small push in +X and release.
2. Apply a small push in -X and release.
3. Reverse quickly from +X to -X.
4. Apply small left/right yaw inputs via force-Y.
5. Confirm stop behavior is smooth and repeatable.

If one axis feels good, lock it and tune the other axis next.

### 5) Important Non-Tunable Internals (Current Code)

These are fixed in `controller_node_refactor.py` right now:

- Force filter coefficients (`alpha_fx`, `alpha_fy`)
- Deadbands for force channels
- Axis blending terms (`blend_strength_x`, `blend_strength_z`)
- Z-axis decel/reversal shaping constants derived from `acc_limit_z`

If your tuning hits a wall, these fixed terms may be the next knobs to expose.

## Validation Rules

Parameter updates are rejected if any of these are violated:

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

## Build And Run

From workspace root:

```bash
colcon build --packages-select arm_controller
source install/setup.bash
```

Run both controller + GUI together:

```bash
ros2 launch arm_controller stiff_tuning.launch.py
```

Optional launch overrides:

```bash
ros2 launch arm_controller stiff_tuning.launch.py \
  controller_node_name:=arm_service \
  odom_topic:=/platform/odometry \
  stop_linear_x_threshold:=0.03 \
  stop_linear_y_threshold:=0.03 \
  stop_angular_z_threshold:=0.05 \
  stop_hold_time_sec:=0.25
```

Run controller:

```bash
ros2 run arm_controller controller_refactor
```

Run GUI (in another terminal):

```bash
source install/setup.bash
ros2 run arm_controller stiff_tuner_gui
```

Optional GUI overrides:

```bash
ros2 run arm_controller stiff_tuner_gui --ros-args \
  -p controller_node_name:=arm_service \
  -p odom_topic:=/platform/odometry \
  -p stop_linear_x_threshold:=0.03 \
  -p stop_linear_y_threshold:=0.03 \
  -p stop_angular_z_threshold:=0.05 \
  -p stop_hold_time_sec:=0.25
```

## GUI Workflow

1. Start `controller_refactor`.
2. Start `stiff_tuner_gui`.
3. Wait until status badge shows `STOPPED`.
4. Edit desired fields.
5. Click `Apply`.
6. If rejected, GUI shows the exact reason returned by the controller and refreshes values from the node.

## CLI Tuning (Headless)

You can also tune without GUI:

```bash
ros2 param list /arm_service | grep stiff_arm
ros2 param get /arm_service stiff_arm.gain_linear_x
ros2 param set /arm_service stiff_arm.gain_linear_x 0.22
```

If the base is moving, `ros2 param set` will fail with a message similar to:

`Base must be stopped for at least 0.25s before tuning parameters.`

## Runtime-Only Behavior

- Parameter updates are applied immediately to control logic.
- No parameter file is written.
- Restarting the controller restores default values from code.

## Troubleshooting

- GUI says `Controller parameter service is unavailable`:
  - Ensure `controller_refactor` is running.
  - Ensure node name matches GUI `controller_node_name` parameter.
- GUI always shows `MOVING`:
  - Check odometry topic is correct and active.
  - Read the velocity line under the status badge to see which odometry component is above threshold.
  - If the base is physically stopped but odometry jitters, raise the relevant `stop_*_threshold`
    parameter slightly and pass the same value to the controller and GUI.
- Apply rejected:
  - Stop the base and retry.
  - Check parameter values satisfy validation rules above.

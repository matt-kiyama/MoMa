# Arm Controller: Live Stiff-Arm Tuning

This package now supports live tuning of stiff-arm controller gains/limits while the controller is running, with a safety lock that only allows parameter updates when the mobile base is stopped.

## What Was Added

- Runtime ROS parameters for all stiff-arm tuning fields under `stiff_arm.*`.
- Safety gate for parameter updates:
  - Uses `ld250_pose` (`nav_msgs/msg/Odometry`).
  - Update accepted only if:
    - `|linear.x| <= 0.01`
    - `|linear.y| <= 0.01`
    - `|angular.z| <= 0.02`
    - conditions held continuously for at least `0.25 s`
- New GUI node for live tuning:
  - executable: `stiff_tuner_gui`
  - node name: `stiff_param_tuner_gui`
- Runtime-only behavior: tuned values are not persisted and return to defaults after restart.

## Nodes And Topics

### `controller_refactor` (`arm_service`)

- Subscribes:
  - `feedback_states` (`tm_msgs/msg/FeedbackState`)
  - `sta_response` (`tm_msgs/msg/StaResponse`)
  - `ld250_pose` (`nav_msgs/msg/Odometry`) for stop/moving detection
- Publishes:
  - `/platform/velocity_command` (`geometry_msgs/msg/Twist`)

### `stiff_tuner_gui` (`stiff_param_tuner_gui`)

- Reads/writes parameters on controller node `arm_service` (configurable).
- Subscribes to odometry (`ld250_pose` by default) to show `STOPPED` / `MOVING` status.

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
  odom_topic:=ld250_pose
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
  -p odom_topic:=ld250_pose
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
  - Verify odometry velocities settle below thresholds for at least `0.25 s`.
- Apply rejected:
  - Stop the base and retry.
  - Check parameter values satisfy validation rules above.

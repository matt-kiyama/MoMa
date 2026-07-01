# Endpoint TCP Controller Guide

This guide explains the alternate safety-demo controller added in:

- `safety/endpoint_control.py`
- `safety/endpoint_controller_node.py`

The short version: instead of following a fixed plan, the controller accepts a
desired TCP endpoint, looks at the current base and arm feedback, then generates
new base and arm commands from the remaining distance to the goal.

For visual flowcharts and sequence diagrams, start with
`ENDPOINT_CONTROLLER_DIAGRAMS.md`.

## Quick Start

Build the workspace after changing `setup.py`:

```bash
colcon build --packages-select safety
source install/setup.bash
```

Start the safety node as usual:

```bash
ros2 run safety safety1
```

Start the endpoint controller with the default target:

```bash
ros2 run safety endpoint_controller
```

Start it with a specific combined TCP target in millimeters:

```bash
ros2 run safety endpoint_controller --ros-args \
  -p target_tcp_position_mm:="[1400.0, -156.0, 600.0]"
```

Update the target while the controller is running:

```bash
ros2 topic pub /target_tcp_position_mm std_msgs/msg/Float64MultiArray \
  "{data: [1400.0, -156.0, 600.0]}"
```

Update position and orientation together:

```bash
ros2 topic pub /target_tcp_position_mm std_msgs/msg/Float64MultiArray \
  "{data: [1400.0, -156.0, 600.0, 3.14, 0.0, 0.0]}"
```

## Safety Path

The controller does not bypass the safety node.

Arm command path:

```text
endpoint_controller
  -> safety_service
  -> safety_node checks/clamps
  -> set_positions
  -> TM driver
```

Base command path:

```text
endpoint_controller
  -> /safety/velocity_command
  -> safety_node checks/clamps
  -> /platform/velocity_command
  -> LD250/base controller
```

This means the endpoint controller proposes commands, but the safety node still
has the final say before those commands reach the robot.

## Files

`safety/endpoint_control.py`

Pure Python command-law code. It has no ROS imports, so it can be unit tested
without a running robot. This file answers: "Given the current robot state and a
TCP endpoint, what arm target and base velocity should we request?"

`safety/endpoint_controller_node.py`

ROS wrapper. It subscribes to feedback, converts units, calls the pure command
law, and sends the resulting commands through the safety node.

`test/test_endpoint_control.py`

Small tests for reachable and far-away x targets.

## Frames And Units

The controller uses millimeters internally.

Inputs from ROS:

- `feedback_states.tool_pose`: arm TCP pose in meters
- `/platform/odometry`: base pose in meters
- `target_tcp_position_mm`: desired combined TCP endpoint in millimeters

Internal state:

```text
combined_tcp_mm = base_position_mm + arm_tcp_position_mm + arm_offset_mm
```

The default fixed arm offset is:

```text
arm_offset_mm = (304.8, 0.0, 387.35)
```

That matches the older safety demo offsets:

- x offset: 12.0 in = 304.8 mm
- y offset: 0.0 mm
- z offset: 15.25 in = 387.35 mm

Outputs to ROS:

- arm `SetPositions.PTP_T` positions are converted back to meters
- base `Twist.linear.x` is published in meters per second

## Control Law

At each timer tick, the controller does this:

1. Compute the current combined TCP position.
2. Compute the distance from the current combined TCP to the requested endpoint.
3. Ask where the arm TCP would need to go if the base stayed still.
4. Clamp that arm target into the configured arm workspace.
5. If x had to be clamped, move the base to make up the remaining x distance.
6. Scale arm velocity from the arm distance to the selected target.
7. Publish base velocity and occasionally send an arm `PTP_T` request.

The important idea is that the arm handles the local target when it can. The
base moves when the target is too far forward or backward for the arm workspace.

## Why Only Base X

The current safety node only clamps and forwards base `linear.x` and
`angular.z`. The endpoint controller currently uses `linear.x` because the old
demo and existing thresholds are x-forward focused.

The y and z components are still included in the arm TCP target and clamped to
the arm workspace. If a target is outside y or z reach, the node logs which axes
were clamped, but it does not currently command lateral base motion or lift
motion.

## Parameters

`target_tcp_position_mm`

Default TCP endpoint in combined space. Format: `[x_mm, y_mm, z_mm]`.

`target_tcp_orientation`

Orientation sent with arm `PTP_T` commands. The controller regulates position,
not orientation, so these values pass through unchanged.

`target_topic`

Topic used for runtime target updates. Default: `target_tcp_position_mm`.

`control_rate_hz`

Main controller loop rate. Default: `10.0`.

`arm_command_period_sec`

Minimum time between arm service requests after the previous request completes.
Default: `0.5`.

`arm_reissue_delta_mm`

Minimum arm target change needed before sending another arm request. Default:
`5.0`.

`arm_margin_mm`

Margin moved inward from the configured arm workspace before selecting targets.
Default: `20.0`.

`base_kp`

Proportional gain for base x motion. The command is:

```text
base_linear_x_mps = base_kp * base_error_x_mm / 1000.0
```

Default: `0.35`.

`base_tolerance_mm`

Deadband around the computed base x setpoint. Default: `10.0`.

`goal_tolerance_mm`

Distance where the combined TCP is considered at the goal. Default: `15.0`.

`arm_min_velocity_mps`, `arm_max_velocity_mps`, `arm_velocity_gain`

Arm TCP velocity is scaled with arm distance:

```text
requested_arm_velocity =
  arm_min_velocity_mps + arm_velocity_gain * arm_distance_mm / 1000.0
```

Then it is clamped between min and max.

## Tuning Order

Tune in this order:

1. Confirm `arm_thresholds.yaml` and `base_thresholds.yaml` match the real safe
   operating limits.
2. Use a reachable target and confirm the arm moves without base motion.
3. Use a far x target and confirm the arm extends while the base moves forward.
4. Lower `base_kp` if the base approaches too aggressively.
5. Raise `base_tolerance_mm` if the base hunts near its setpoint.
6. Lower `arm_max_velocity_mps` if arm moves feel too fast.
7. Increase `arm_command_period_sec` if the arm driver gets too many requests.

## Debugging Checklist

No motion:

- Confirm `safety1` is running.
- Confirm `feedback_states` is publishing.
- Confirm `/platform/odometry` is publishing.
- Watch logs for `Waiting for feedback`.
- Watch logs for `safety_service is not available`.

Arm target gets clamped:

- Check the log line `TCP target requires clamping arm axis/axes`.
- If only x is clamped, the base should move to compensate.
- If y or z is clamped, the endpoint may be outside the current arm workspace.

Base moves too fast:

- Lower `base_kp`.
- Lower the max x velocity in `base_thresholds.yaml`.

Arm gets too many commands:

- Increase `arm_command_period_sec`.
- Increase `arm_reissue_delta_mm`.

## Mental Model

Think of the controller as choosing a point inside the arm's box of reach. If the
goal is inside that box, the base stays still and the arm goes there. If the goal
is outside the box in x, the arm goes to the nearest reachable x point and the
base drives until that reachable point lines up with the requested endpoint.

The safety node remains between this controller and the real robot, so this
controller is not the final authority on what motion is allowed.

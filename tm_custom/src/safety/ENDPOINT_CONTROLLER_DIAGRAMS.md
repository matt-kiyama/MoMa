# Endpoint Controller Diagrams

These diagrams show how the safety demo works at the system level and inside
the endpoint controller.

## 1. Safety Demo Overview

This is the big picture. The endpoint controller proposes motion, but both arm
and base commands still pass through `safety_node` before reaching the robot.

```mermaid
flowchart LR
    operator["Operator / demo script<br/>TCP endpoint in mm"]
    target_topic["/target_tcp_position_mm<br/>Float64MultiArray"]
    endpoint["endpoint_controller<br/>closed-loop TCP controller"]

    feedback_arm["feedback_states<br/>TM arm TCP feedback"]
    feedback_base["/platform/odometry<br/>LD250 base feedback"]

    safety_service["safety_service<br/>SetPositions service"]
    safety_vel["/safety/velocity_command<br/>Twist input"]
    safety_node["safety_node<br/>checks and clamps commands"]

    set_positions["set_positions<br/>TM driver service"]
    platform_vel["/platform/velocity_command<br/>base velocity output"]

    arm["TM arm"]
    base["LD250 base"]
    combined_tcp["Combined TCP position<br/>base + arm offset + arm TCP"]

    operator --> target_topic --> endpoint
    feedback_arm --> endpoint
    feedback_base --> endpoint

    endpoint --> safety_service --> safety_node --> set_positions --> arm
    endpoint --> safety_vel --> safety_node --> platform_vel --> base

    arm --> feedback_arm
    base --> feedback_base
    feedback_arm --> combined_tcp
    feedback_base --> combined_tcp
    combined_tcp --> endpoint
```

## 2. Command Paths Through The Safety Node

The arm and base use different ROS interfaces, but they share the same safety
idea: the endpoint controller does not talk directly to the final actuator
interfaces.

```mermaid
flowchart TB
    subgraph endpoint_controller["endpoint_controller"]
        law["EndpointControlLaw.compute()"]
        arm_request["Build PTP_T<br/>SetPositions.Request"]
        base_twist["Build Twist<br/>linear.x only"]
    end

    subgraph safety_node["safety_node"]
        arm_check["Clamp TCP x/y/z<br/>Clamp TCP velocity"]
        base_check["Clamp base linear.x<br/>Clamp base angular.z"]
    end

    subgraph final_outputs["Robot-facing outputs"]
        arm_driver["set_positions"]
        base_driver["/platform/velocity_command"]
    end

    law --> arm_request -->|"safety_service"| arm_check --> arm_driver
    law --> base_twist -->|"/safety/velocity_command"| base_check --> base_driver
```

## 3. Endpoint Controller Internals

This shows the ROS wrapper and the pure Python command law. The wrapper handles
topics, services, and unit conversions. The command law handles the math.

```mermaid
flowchart LR
    subgraph ros_inputs["ROS inputs"]
        target["target_tcp_position_mm<br/>already in mm"]
        arm_feedback["feedback_states.tool_pose<br/>meters"]
        base_feedback["/platform/odometry<br/>meters"]
    end

    subgraph node["endpoint_controller_node.py"]
        convert_arm["Convert arm TCP<br/>m to mm"]
        convert_base["Convert base pose<br/>m to mm"]
        state["EndpointRobotState<br/>base_position_mm<br/>arm_tcp_position_mm"]
        config["EndpointControlConfig<br/>thresholds and gains"]
    end

    subgraph law["endpoint_control.py"]
        combined["combined_tcp_mm =<br/>base + arm_offset + arm_tcp"]
        raw_arm["raw_arm_target =<br/>target - base - arm_offset"]
        clamp_arm["Clamp target into<br/>arm workspace"]
        base_error["Solve base x error<br/>from remaining x distance"]
        velocity["Scale arm velocity<br/>from arm distance"]
        command["EndpointCommand<br/>arm target + base velocity"]
    end

    subgraph ros_outputs["ROS outputs"]
        arm_out["safety_service<br/>PTP_T request"]
        base_out["/safety/velocity_command<br/>Twist"]
    end

    arm_feedback --> convert_arm --> state
    base_feedback --> convert_base --> state
    target --> combined
    state --> combined
    config --> clamp_arm
    config --> base_error
    config --> velocity

    combined --> raw_arm --> clamp_arm --> base_error --> velocity --> command
    command --> arm_out
    command --> base_out
```

## 4. Control Law Decision Flow

This is the logic that runs every controller tick.

```mermaid
flowchart TD
    start["Timer tick"]
    feedback_ready{"Have arm feedback<br/>and base odometry?"}
    wait["Wait and log missing topics"]
    combined["Compute combined TCP<br/>base + offset + arm TCP"]
    distance["Compute distance to endpoint"]
    raw_arm["Compute raw arm target<br/>assuming base stays still"]
    clamp["Clamp arm target<br/>inside shrunken workspace"]
    goal{"Inside goal tolerance?"}
    stop_base["Publish zero base velocity"]
    solve_base["Solve base x setpoint<br/>for selected arm target"]
    base_deadband{"Base x error inside<br/>base tolerance?"}
    base_zero["Set base velocity = 0"]
    base_p["Set base velocity =<br/>base_kp * error / 1000"]
    base_limit["Clamp base velocity<br/>to base thresholds"]
    arm_speed["Scale arm velocity<br/>from arm target distance"]
    send_guard{"Arm request allowed?<br/>not pending + target moved"}
    skip_arm["Skip arm request this tick"]
    send_arm["Send PTP_T through<br/>safety_service"]
    publish_base["Publish Twist through<br/>/safety/velocity_command"]

    start --> feedback_ready
    feedback_ready -- "no" --> wait
    feedback_ready -- "yes" --> combined --> distance --> raw_arm --> clamp --> goal
    goal -- "yes" --> stop_base --> publish_base
    goal -- "no" --> solve_base --> base_deadband
    base_deadband -- "yes" --> base_zero --> arm_speed
    base_deadband -- "no" --> base_p --> base_limit --> arm_speed
    arm_speed --> send_guard
    send_guard -- "no" --> skip_arm --> publish_base
    send_guard -- "yes" --> send_arm --> publish_base
```

## 5. One Controller Tick Sequence

This sequence view is useful when debugging timing. Base commands are published
every tick. Arm commands are only sent when the request throttle allows it.

```mermaid
sequenceDiagram
    participant Base as LD250 base
    participant Arm as TM arm
    participant Controller as endpoint_controller
    participant Safety as safety_node
    participant Driver as TM/base drivers

    Base->>Controller: /platform/odometry
    Arm->>Controller: feedback_states
    Controller->>Controller: compute combined TCP
    Controller->>Controller: compute arm target and base velocity
    Controller->>Safety: /safety/velocity_command
    Safety->>Driver: /platform/velocity_command

    alt arm request throttle allows command
        Controller->>Safety: safety_service SetPositions.PTP_T
        Safety->>Safety: clamp TCP position and velocity
        Safety->>Driver: set_positions
        Driver->>Arm: execute arm motion
    else request pending or target change too small
        Controller->>Controller: keep waiting
    end
```

## 6. Frame And Unit Relationship

The endpoint target is in the combined TCP frame used by this demo. The
controller combines base odometry, fixed arm mount offset, and arm TCP feedback.

```mermaid
flowchart LR
    base_origin["Base odometry position<br/>/platform/odometry<br/>meters to mm"]
    arm_offset["Fixed arm mount offset<br/>(304.8, 0.0, 387.35) mm"]
    arm_tcp["Arm TCP feedback<br/>feedback_states.tool_pose<br/>meters to mm"]
    combined["Current combined TCP<br/>millimeters"]
    target["Requested endpoint<br/>target_tcp_position_mm<br/>millimeters"]
    error["Goal error<br/>target - combined"]

    base_origin --> combined
    arm_offset --> combined
    arm_tcp --> combined
    target --> error
    combined --> error
```

## 7. Reachable Vs. Far X Target

The same command law handles both cases.

```mermaid
flowchart TB
    target["Requested TCP endpoint"]
    raw["Raw arm target<br/>target - base - offset"]
    inside{"Raw target inside<br/>arm workspace?"}
    arm_only["Arm target = raw target<br/>base velocity = 0"]
    clamp_x["Arm target clamped<br/>near workspace x edge"]
    base_move["Base moves in x<br/>to make up remaining distance"]
    safety["Both commands still pass<br/>through safety_node"]

    target --> raw --> inside
    inside -- "yes" --> arm_only --> safety
    inside -- "no, x outside" --> clamp_x --> base_move --> safety
```

## Reading The Logs

Useful status messages from `endpoint_controller`:

- `Waiting for feedback`: one or both feedback topics have not arrived yet.
- `Endpoint TCP controller ready`: the node started and created its interfaces.
- `distance=... base_x=... arm_target=...`: current command-law status.
- `TCP target requires clamping arm axis/axes`: target is outside the arm-only
  reachable workspace on the listed axis or axes.
- `safety_service is not available`: the controller is holding arm commands
  until `safety_node` is running.

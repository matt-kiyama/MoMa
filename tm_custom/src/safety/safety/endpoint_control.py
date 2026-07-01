"""Pure endpoint-to-command control law for the safety demo.

This module intentionally has no ROS imports.  It turns a desired TCP endpoint
and the latest robot state into two things:

1. A TCP-space arm target, still expressed in the arm's local TCP frame.
2. A base x velocity that helps place the arm workspace around the target.

Keeping the math isolated makes it easy to unit test and reason about before
the ROS node sends commands through the safety node.
"""

from dataclasses import dataclass
from math import sqrt
from typing import Sequence, Tuple


# All endpoint math in this module uses millimeters unless a field name says
# otherwise.  ROS messages are converted at the node boundary.
Vector3 = Tuple[float, float, float]


def clamp(value: float, lower: float, upper: float) -> float:
    """Limit a scalar value to an inclusive [lower, upper] range."""
    return max(lower, min(upper, value))


def vector_distance(a: Sequence[float], b: Sequence[float]) -> float:
    """Return Euclidean distance between two vectors of matching length."""
    return sqrt(sum((left - right) ** 2 for left, right in zip(a, b)))


@dataclass(frozen=True)
class AxisLimits:
    """Minimum and maximum motion range for one linear axis."""

    minimum: float
    maximum: float

    def clamp(self, value: float) -> float:
        """Clamp a value to this axis' allowed range."""
        return clamp(value, self.minimum, self.maximum)

    def shrink(self, margin: float) -> "AxisLimits":
        """Return limits moved inward by a safety margin.

        If the margin is larger than the available range, the original limits
        are returned so the controller does not invert the workspace.
        """
        if 2.0 * margin >= (self.maximum - self.minimum):
            return self
        return AxisLimits(self.minimum + margin, self.maximum - margin)


@dataclass(frozen=True)
class ArmWorkspace:
    """Reachable TCP-space box for the arm, in millimeters."""

    x: AxisLimits
    y: AxisLimits
    z: AxisLimits


@dataclass(frozen=True)
class BaseVelocityLimits:
    """Base x velocity limits in meters per second."""

    linear_x_min: float
    linear_x_max: float


@dataclass(frozen=True)
class EndpointControlConfig:
    """Tunable constants used by the endpoint controller."""

    # Arm workspace is loaded from arm_thresholds.yaml.
    arm_workspace: ArmWorkspace

    # Base velocity limits are loaded from base_thresholds.yaml.
    base_velocity_limits: BaseVelocityLimits

    # Fixed transform from the base odometry frame to the arm TCP frame origin.
    arm_offset_mm: Vector3 = (304.8, 0.0, 387.35)

    # Inward margin applied to the arm workspace before choosing a command.
    arm_margin_mm: float = 20.0

    # Proportional gain for base x motion.  Output is converted from mm/s to m/s.
    base_kp: float = 0.35

    # Deadband around the computed base x setpoint.
    base_tolerance_mm: float = 10.0

    # Overall TCP distance at which the controller considers the goal reached.
    goal_tolerance_mm: float = 15.0

    # Arm command velocity bounds and distance-based velocity slope.
    arm_min_velocity_mps: float = 0.05
    arm_max_velocity_mps: float = 0.25
    arm_velocity_gain: float = 0.30


@dataclass(frozen=True)
class EndpointRobotState:
    """Current base and arm feedback expressed in millimeters."""

    # Base position from /platform/odometry, converted to millimeters.
    base_position_mm: Vector3

    # Current arm TCP pose from feedback_states, converted to millimeters.
    arm_tcp_position_mm: Vector3

    def combined_tcp_position_mm(self, arm_offset_mm: Vector3) -> Vector3:
        """Compute the TCP position in the combined base/world frame."""
        return (
            self.base_position_mm[0] + self.arm_tcp_position_mm[0] + arm_offset_mm[0],
            self.base_position_mm[1] + self.arm_tcp_position_mm[1] + arm_offset_mm[1],
            self.base_position_mm[2] + self.arm_tcp_position_mm[2] + arm_offset_mm[2],
        )


@dataclass(frozen=True)
class EndpointCommand:
    """Controller output consumed by the ROS node."""

    # Arm target in millimeters; the node converts this to meters for PTP_T.
    arm_target_mm: Vector3

    # Arm TCP velocity in meters per second for SetPositions.Request.velocity.
    arm_velocity_mps: float

    # Base linear.x command in meters per second.
    base_linear_x_mps: float

    # Current combined TCP position, useful for status logging.
    combined_tcp_position_mm: Vector3

    # target - current combined TCP, in millimeters.
    goal_error_mm: Vector3

    # Magnitude of goal_error_mm.
    distance_to_goal_mm: float

    # Distance from current arm TCP to the selected arm target.
    arm_distance_mm: float

    # True when the combined TCP is inside the goal tolerance.
    at_goal: bool

    # Axis names where the requested arm target exceeded the arm workspace.
    clamped_axes: Tuple[str, ...]


class EndpointControlLaw:
    """Compute base and arm commands from a TCP endpoint."""

    def __init__(self, config: EndpointControlConfig):
        self.config = config

    def compute(self, state: EndpointRobotState, target_tcp_position_mm: Sequence[float]) -> EndpointCommand:
        """Generate one closed-loop command for the current feedback sample."""

        # Normalize the target to a fixed-length tuple so downstream code does
        # not depend on whether ROS passed in a list, tuple, or array-like value.
        target = (target_tcp_position_mm[0], target_tcp_position_mm[1], target_tcp_position_mm[2])

        # The combined TCP is where the tool is in the same frame as the target:
        # base odometry + fixed arm offset + arm TCP feedback.
        combined = state.combined_tcp_position_mm(self.config.arm_offset_mm)
        error = (
            target[0] - combined[0],
            target[1] - combined[1],
            target[2] - combined[2],
        )
        distance_to_goal = vector_distance(target, combined)

        # First ask: "If the base stayed exactly where it is, where would the
        # arm TCP need to go to hit the endpoint?"
        raw_arm_target = (
            target[0] - state.base_position_mm[0] - self.config.arm_offset_mm[0],
            target[1] - state.base_position_mm[1] - self.config.arm_offset_mm[1],
            target[2] - state.base_position_mm[2] - self.config.arm_offset_mm[2],
        )

        # Pull the workspace limits inward slightly so ordinary commands do not
        # live exactly on the configured safety boundary.
        x_limits = self.config.arm_workspace.x.shrink(self.config.arm_margin_mm)
        y_limits = self.config.arm_workspace.y.shrink(self.config.arm_margin_mm)
        z_limits = self.config.arm_workspace.z.shrink(self.config.arm_margin_mm)

        # The arm target is the closest point inside the shrunken workspace.
        # If the endpoint is outside arm reach, the remaining x error is handed
        # to the base controller below.
        arm_target = (
            x_limits.clamp(raw_arm_target[0]),
            y_limits.clamp(raw_arm_target[1]),
            z_limits.clamp(raw_arm_target[2]),
        )

        # Track clamped axes so the ROS node can warn when the requested endpoint
        # cannot be reached by the arm alone.
        clamped_axes = tuple(
            axis
            for axis, raw_value, clamped_value in zip(("x", "y", "z"), raw_arm_target, arm_target)
            if abs(raw_value - clamped_value) > 1e-6
        )

        # Once the arm target is chosen, solve for the base x position that
        # would put that arm target exactly under the requested endpoint.
        base_target_x = target[0] - self.config.arm_offset_mm[0] - arm_target[0]
        base_error_x = base_target_x - state.base_position_mm[0]

        # Stop base motion near the setpoint or once the combined TCP is already
        # close enough to the endpoint.
        if abs(base_error_x) <= self.config.base_tolerance_mm or distance_to_goal <= self.config.goal_tolerance_mm:
            base_linear_x_mps = 0.0
        else:
            # Proportional base command: gain * mm_error, then convert mm/s to
            # m/s because geometry_msgs/Twist.linear.x is in meters per second.
            requested = self.config.base_kp * base_error_x / 1000.0
            base_linear_x_mps = clamp(
                requested,
                self.config.base_velocity_limits.linear_x_min,
                self.config.base_velocity_limits.linear_x_max,
            )

        # Scale arm speed with remaining arm travel.  Farther moves run faster,
        # short corrections slow down automatically.
        arm_distance = vector_distance(state.arm_tcp_position_mm, arm_target)
        requested_arm_velocity = self.config.arm_min_velocity_mps + self.config.arm_velocity_gain * arm_distance / 1000.0
        arm_velocity_mps = clamp(
            requested_arm_velocity,
            self.config.arm_min_velocity_mps,
            self.config.arm_max_velocity_mps,
        )

        return EndpointCommand(
            arm_target_mm=arm_target,
            arm_velocity_mps=arm_velocity_mps,
            base_linear_x_mps=base_linear_x_mps,
            combined_tcp_position_mm=combined,
            goal_error_mm=error,
            distance_to_goal_mm=distance_to_goal,
            arm_distance_mm=arm_distance,
            at_goal=distance_to_goal <= self.config.goal_tolerance_mm,
            clamped_axes=clamped_axes,
        )

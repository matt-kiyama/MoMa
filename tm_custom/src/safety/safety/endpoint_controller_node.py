"""ROS node for the endpoint TCP controller.

The node is deliberately thin: it gathers ROS feedback, calls the pure
EndpointControlLaw, and sends the resulting commands through the existing safety
node interfaces.

Arm path:
    endpoint_controller -> safety_service -> set_positions -> TM driver

Base path:
    endpoint_controller -> /safety/velocity_command -> safety_node ->
    /platform/velocity_command
"""

from pathlib import Path
from typing import Sequence

import rclpy
import yaml
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from std_msgs.msg import Float64MultiArray
from tm_msgs.msg import FeedbackState
from tm_msgs.srv import SetPositions

from .endpoint_control import (
    ArmWorkspace,
    AxisLimits,
    BaseVelocityLimits,
    EndpointControlConfig,
    EndpointControlLaw,
    EndpointRobotState,
    vector_distance,
)


CONFIG_DIR = Path(__file__).resolve().parent


def load_arm_workspace(path: Path) -> ArmWorkspace:
    """Load arm TCP workspace limits from arm_thresholds.yaml.

    The YAML stores Cartesian ranges in millimeters.  The pure control law also
    works in millimeters, so no conversion is needed here.
    """
    with path.open("r") as file:
        data = yaml.safe_load(file)

    return ArmWorkspace(
        x=AxisLimits(data["x_range"][0], data["x_range"][1]),
        y=AxisLimits(data["y_range"][0], data["y_range"][1]),
        z=AxisLimits(data["z_range"][0], data["z_range"][1]),
    )


def load_base_velocity_limits(path: Path) -> BaseVelocityLimits:
    """Load the base x velocity limits used before publishing Twist commands."""
    with path.open("r") as file:
        data = yaml.safe_load(file)

    return BaseVelocityLimits(
        linear_x_min=data["x_linear"][0],
        linear_x_max=data["x_linear"][1],
    )


class EndpointTcpController(Node):
    """Closed-loop controller that drives a requested combined TCP endpoint."""

    def __init__(self):
        super().__init__("endpoint_tcp_controller")

        # Desired combined TCP endpoint, in millimeters, relative to the same
        # combined frame used by the old safety demo.
        self.declare_parameter("target_tcp_position_mm", [1400.0, -156.0, 600.0])

        # Orientation sent with PTP_T arm requests.  The control law currently
        # regulates position only; orientation passes through unchanged.
        self.declare_parameter("target_tcp_orientation", [3.14, 0.0, 0.0])

        # Optional runtime target topic.  Publish std_msgs/Float64MultiArray
        # with [x_mm, y_mm, z_mm] or [x_mm, y_mm, z_mm, rx, ry, rz].
        self.declare_parameter("target_topic", "target_tcp_position_mm")

        # Main loop rate.  Arm commands are throttled separately below.
        self.declare_parameter("control_rate_hz", 10.0)

        # Minimum time between arm SetPositions calls once a request finishes.
        self.declare_parameter("arm_command_period_sec", 0.5)

        # Minimum target change before reissuing an arm command.
        self.declare_parameter("arm_reissue_delta_mm", 5.0)

        # Command-law tuning parameters.  See ENDPOINT_CONTROLLER_GUIDE.md for
        # the practical meaning of each parameter.
        self.declare_parameter("arm_margin_mm", 20.0)
        self.declare_parameter("base_kp", 0.35)
        self.declare_parameter("base_tolerance_mm", 10.0)
        self.declare_parameter("goal_tolerance_mm", 15.0)
        self.declare_parameter("arm_min_velocity_mps", 0.05)
        self.declare_parameter("arm_max_velocity_mps", 0.25)
        self.declare_parameter("arm_velocity_gain", 0.30)

        # Convert the existing YAML safety ranges into the small config object
        # that the pure control law expects.
        arm_workspace = load_arm_workspace(CONFIG_DIR / "arm_thresholds.yaml")
        base_velocity_limits = load_base_velocity_limits(CONFIG_DIR / "base_thresholds.yaml")
        self.control_law = EndpointControlLaw(
            EndpointControlConfig(
                arm_workspace=arm_workspace,
                base_velocity_limits=base_velocity_limits,
                arm_margin_mm=self.get_parameter("arm_margin_mm").value,
                base_kp=self.get_parameter("base_kp").value,
                base_tolerance_mm=self.get_parameter("base_tolerance_mm").value,
                goal_tolerance_mm=self.get_parameter("goal_tolerance_mm").value,
                arm_min_velocity_mps=self.get_parameter("arm_min_velocity_mps").value,
                arm_max_velocity_mps=self.get_parameter("arm_max_velocity_mps").value,
                arm_velocity_gain=self.get_parameter("arm_velocity_gain").value,
            )
        )

        self.target_tcp_position_mm = self._parameter_array("target_tcp_position_mm", 3)
        self.target_tcp_orientation = self._parameter_array("target_tcp_orientation", 3)
        self.arm_command_period_sec = float(self.get_parameter("arm_command_period_sec").value)
        self.arm_reissue_delta_mm = float(self.get_parameter("arm_reissue_delta_mm").value)

        # Feedback starts as unavailable.  The controller holds commands until
        # both base odometry and arm TCP feedback have arrived.
        self.base_position_mm = None
        self.arm_tcp_position_mm = None

        # Arm command bookkeeping prevents flooding safety_service every timer
        # tick while a previous command is still in flight.
        self.last_arm_target_mm = None
        self.last_arm_command_time = None
        self.pending_arm_future = None

        # Status logging state.  Logs are throttled to stay readable.
        self.last_status_log_time = None
        self.last_clamped_axes = ()

        # Safety-preserving outputs.  Do not call set_positions directly here:
        # safety_service clamps/checks arm commands before forwarding them.
        self.safety_client = self.create_client(SetPositions, "safety_service")
        self.twist_publisher = self.create_publisher(Twist, "/safety/velocity_command", 10)

        # Feedback subscriptions.  FeedbackState.tool_pose is in meters; odom
        # pose is also in meters, so callbacks convert both to millimeters.
        self.create_subscription(FeedbackState, "feedback_states", self.arm_feedback_callback, 10)
        self.create_subscription(Odometry, "/platform/odometry", self.base_feedback_callback, qos_profile_sensor_data)

        # Runtime target updates are intentionally simple so a demo operator can
        # publish a target from the command line without a custom message type.
        self.create_subscription(
            Float64MultiArray,
            str(self.get_parameter("target_topic").value),
            self.target_callback,
            10,
        )

        # Start the closed-loop controller after all publishers, subscribers,
        # service clients, and state variables exist.
        control_rate_hz = float(self.get_parameter("control_rate_hz").value)
        self.timer = self.create_timer(1.0 / control_rate_hz, self.control_loop)
        self.get_logger().info(
            "Endpoint TCP controller ready; commands route through safety_service and /safety/velocity_command"
        )

    def _parameter_array(self, name: str, expected_length: int):
        """Read a ROS parameter that must contain a fixed-length numeric array."""
        values = list(self.get_parameter(name).value)
        if len(values) != expected_length:
            raise ValueError(f"{name} must have exactly {expected_length} values")
        return tuple(float(value) for value in values)

    def arm_feedback_callback(self, msg: FeedbackState):
        """Store the current arm TCP position from TM feedback in millimeters."""
        if len(msg.tool_pose) < 3:
            return
        self.arm_tcp_position_mm = (
            msg.tool_pose[0] * 1000.0,
            msg.tool_pose[1] * 1000.0,
            msg.tool_pose[2] * 1000.0,
        )

    def base_feedback_callback(self, msg: Odometry):
        """Store the current base odometry position in millimeters."""
        self.base_position_mm = (
            msg.pose.pose.position.x * 1000.0,
            msg.pose.pose.position.y * 1000.0,
            msg.pose.pose.position.z * 1000.0,
        )

    def target_callback(self, msg: Float64MultiArray):
        """Accept a new TCP endpoint from a runtime topic."""
        if len(msg.data) < 3:
            self.get_logger().warn("Ignoring target_tcp_position_mm message with fewer than 3 values")
            return

        # First three values are always the endpoint position in millimeters.
        self.target_tcp_position_mm = tuple(float(value) for value in msg.data[:3])

        # Optional values four through six override the orientation for future
        # arm requests.
        if len(msg.data) >= 6:
            self.target_tcp_orientation = tuple(float(value) for value in msg.data[3:6])
        self.get_logger().info(
            "Updated TCP target to "
            f"[{self.target_tcp_position_mm[0]:.1f}, {self.target_tcp_position_mm[1]:.1f}, "
            f"{self.target_tcp_position_mm[2]:.1f}] mm"
        )

    def control_loop(self):
        """Run one controller tick."""

        # The command law needs both feedback sources to compute a combined TCP.
        if self.base_position_mm is None or self.arm_tcp_position_mm is None:
            self._log_waiting_for_feedback()
            return

        # Build a plain Python state object and let endpoint_control.py do the
        # actual command-law math.
        state = EndpointRobotState(
            base_position_mm=self.base_position_mm,
            arm_tcp_position_mm=self.arm_tcp_position_mm,
        )
        command = self.control_law.compute(state, self.target_tcp_position_mm)

        # Publish base motion on the safety input topic.  The safety node will
        # clamp and forward this to /platform/velocity_command.
        twist = Twist()
        twist.linear.x = command.base_linear_x_mps
        self.twist_publisher.publish(twist)

        # If the combined TCP is already close enough, keep publishing zero base
        # velocity and avoid sending another arm command.
        if command.at_goal:
            self._log_status(command.distance_to_goal_mm, command.base_linear_x_mps, command.arm_target_mm)
            return

        # Warn once each time the set of saturated arm axes changes.  Persistent
        # clamping usually means the endpoint needs base movement or is outside
        # the current y/z workspace.
        if command.clamped_axes and command.clamped_axes != self.last_clamped_axes:
            self.get_logger().warn(
                "TCP target requires clamping arm axis/axes: " + ", ".join(command.clamped_axes)
            )
        self.last_clamped_axes = command.clamped_axes

        # Arm service calls are discrete and slower than the timer.  The guard
        # below keeps a steady control loop without stacking service requests.
        if self._should_send_arm_command(command.arm_target_mm):
            self._send_arm_command(command.arm_target_mm, command.arm_velocity_mps)

        self._log_status(command.distance_to_goal_mm, command.base_linear_x_mps, command.arm_target_mm)

    def _log_waiting_for_feedback(self):
        """Throttle startup logs while feedback topics are still missing."""
        now = self.get_clock().now()
        if self.last_status_log_time is None or (now - self.last_status_log_time).nanoseconds > 2_000_000_000:
            missing = []
            if self.base_position_mm is None:
                missing.append("/platform/odometry")
            if self.arm_tcp_position_mm is None:
                missing.append("feedback_states")
            self.get_logger().info("Waiting for feedback: " + ", ".join(missing))
            self.last_status_log_time = now

    def _log_status(self, distance_to_goal_mm: float, base_linear_x_mps: float, arm_target_mm: Sequence[float]):
        """Throttle compact status logs during motion."""
        now = self.get_clock().now()
        if self.last_status_log_time is None or (now - self.last_status_log_time).nanoseconds > 2_000_000_000:
            self.get_logger().info(
                f"distance={distance_to_goal_mm:.1f} mm, "
                f"base_x={base_linear_x_mps:.3f} m/s, "
                f"arm_target=[{arm_target_mm[0]:.1f}, {arm_target_mm[1]:.1f}, {arm_target_mm[2]:.1f}] mm"
            )
            self.last_status_log_time = now

    def _should_send_arm_command(self, arm_target_mm: Sequence[float]) -> bool:
        """Return True when it is time to issue another arm PTP_T request."""

        # Never stack a second SetPositions request while one is unresolved.
        if self.pending_arm_future is not None and not self.pending_arm_future.done():
            return False

        now = self.get_clock().now()

        # Send the first command as soon as feedback and safety_service are ready.
        if self.last_arm_target_mm is None or self.last_arm_command_time is None:
            return True

        # Reissue only if the target moved enough and enough time has passed.
        # This keeps the arm tracking a moving base without flooding the driver.
        target_delta = vector_distance(self.last_arm_target_mm, arm_target_mm)
        elapsed_sec = (now - self.last_arm_command_time).nanoseconds / 1_000_000_000.0
        return target_delta >= self.arm_reissue_delta_mm and elapsed_sec >= self.arm_command_period_sec

    def _send_arm_command(self, arm_target_mm: Sequence[float], velocity_mps: float):
        """Send one arm target through safety_service."""

        # Holding the command is better than bypassing the safety node.  Once the
        # service appears, the next controller tick will try again.
        if not self.safety_client.wait_for_service(timeout_sec=0.0):
            self.get_logger().warn("safety_service is not available; holding arm command")
            return

        # safety_service expects the same SetPositions request type as the TM
        # driver.  PTP_T positions are [x_m, y_m, z_m, rx, ry, rz].
        request = SetPositions.Request()
        request.motion_type = SetPositions.Request.PTP_T
        request.positions = [
            arm_target_mm[0] / 1000.0,
            arm_target_mm[1] / 1000.0,
            arm_target_mm[2] / 1000.0,
            self.target_tcp_orientation[0],
            self.target_tcp_orientation[1],
            self.target_tcp_orientation[2],
        ]
        request.velocity = float(velocity_mps)
        request.acc_time = 0.1
        request.blend_percentage = 0
        request.fine_goal = False

        # Store the future and the commanded target so the throttle in
        # _should_send_arm_command has something to compare against.
        self.pending_arm_future = self.safety_client.call_async(request)
        self.pending_arm_future.add_done_callback(self._arm_command_done)
        self.last_arm_target_mm = tuple(float(value) for value in arm_target_mm)
        self.last_arm_command_time = self.get_clock().now()

    def _arm_command_done(self, future):
        """Report rejected or failed safety_service calls."""
        try:
            result = future.result()
            if result is not None and not result.ok:
                self.get_logger().warn("safety_service rejected arm command")
        except Exception as exc:
            self.get_logger().error(f"safety_service arm command failed: {exc}")


def main(args=None):
    """ROS entry point registered as `ros2 run safety endpoint_controller`."""
    rclpy.init(args=args)
    controller = EndpointTcpController()
    rclpy.spin(controller)
    controller.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

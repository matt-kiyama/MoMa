import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist

from tm_msgs.msg import FeedbackState
from tm_msgs.msg import StaResponse

from dataclasses import dataclass
import numpy as np

class EMA:
    def __init__(self, alpha):
        self.alpha = alpha
        self.value = 0.0

    def update(self, new_value):
        self.value = self.alpha * new_value + (1.0 - self.alpha) * self.value
        return self.value

# Create EMA objects
linear_x_ema = EMA(alpha=0.1)
angular_z_ema = EMA(alpha=0.1)

@dataclass
class StiffArmParams:
    """Parameters for the stiff-arm control behavior."""

    force_max: float = 60.0  # newtons
    force_min: float = -60.0  # newtons
    vel_max_z: float = 0.020  # m/s
    vel_min_z: float = -0.020  # m/s
    vel_max_x: float = 0.020  # m/s
    vel_min_x: float = -0.020  # m/s
    gain_linear_x: float = 0.15
    gain_angular_z: float = 1.8

    # NEW: acceleration limits
    acc_limit_x: float = 0.05      # m/s^2
    acc_limit_z: float = 0.3       # rad/s^2


def clamp(value: float, lower: float, upper: float) -> float:
    """Clamp a value between lower and upper bounds."""
    print(value, lower, upper)

    return max(min(value, upper), lower)


class ArmService(Node):

    def __init__(self):
        super().__init__("arm_service")

        self.params = StiffArmParams()

        # Subscriptions
        self.feedback_subscription = self.create_subscription(
            FeedbackState, "feedback_states", self.feedback_callback, 1000
        )

        self.sta_subscription = self.create_subscription(
            StaResponse, "sta_response", self.sta_callback, 10
        )

        self.feedback_subscription
        self.sta_subscription

        # Publisher
        self.twist_publisher = self.create_publisher(Twist, "/platform/velocity_command", 10)

        self.cur_pos_cartesian = np.array([])
        self.tool_pose = np.array([])
        self.current_tag = 0
        self.zero_vels_count = 0
        self.sta_response_val = False

        self.declare_parameter("angle", 91.0)

        # Acceleration limiting variables
        self.prev_vx = 0.0
        self.prev_wz = 0.0
        self.prev_time = self.get_clock().now()

    def limit_rate(self, desired, previous, rate_limit, dt):
        max_delta = rate_limit * dt
        delta = desired - previous
        delta = clamp(delta, -max_delta, max_delta)
        return previous + delta


    def feedback_callback(self, msg):
        self.cur_pos_cartesian = np.asarray(msg.tool_pose)
        self.tcp_force = np.asarray(msg.tcp_force)
        self._stiff_arm_control()

    def sta_callback(self, msg):
        """
        Called if ask_sta (sta_request) is made.
        If ask is made, check if the current queue tag is true, indicates previous motion is complete, then set sta_response_val true
        If current queue tag is false, then set sta_response_val false
        """
        if "true" and str(self.current_tag) in msg.subdata:
            self.sta_response_val = True
        else:
            self.sta_response_val = False

    def _stiff_arm_control(self):
        p = self.params
        current_twist = Twist()

        # --- Time step calculation ---
        now = self.get_clock().now()
        dt = (now - self.prev_time).nanoseconds * 1e-9
        self.prev_time = now

        # Guard against bad timing (startup / pauses)
        if dt <= 0.0 or dt > 0.1:
            dt = 0.01

        # --- Force processing ---
        tcp_fx = clamp(self.tcp_force[0], p.force_min, p.force_max)
        tcp_fy = clamp(self.tcp_force[1], p.force_min, p.force_max)

        # Deadband to prevent drift
        if abs(tcp_fx) < 0.4:
            tcp_fx = 0.0
        if abs(tcp_fy) < 0.4:
            tcp_fy = 0.0

        # --- Desired velocity from force ---
        vx_des = tcp_fx * p.gain_linear_x
        wz_des = tcp_fy * p.gain_angular_z

        # --- Acceleration limiting (slew rate) ---
        vx = self.limit_rate(
            desired=vx_des,
            previous=self.prev_vx,
            rate_limit=p.acc_limit_x,
            dt=dt
        )

        wz = self.limit_rate(
            desired=wz_des,
            previous=self.prev_wz,
            rate_limit=p.acc_limit_z,
            dt=dt
        )

        # --- Velocity limits ---
        vx = clamp(vx, p.vel_min_x, p.vel_max_x)
        wz = clamp(wz, p.vel_min_z, p.vel_max_z)

        # Save for next cycle
        self.prev_vx = vx
        self.prev_wz = wz

        # --- Publish ---
        current_twist.linear.x = vx
        current_twist.angular.z = wz
        self.twist_publisher.publish(current_twist)


def main(args=None):
    rclpy.init(args=args)

    arm_service = ArmService()

    rclpy.spin(arm_service)

    arm_service.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

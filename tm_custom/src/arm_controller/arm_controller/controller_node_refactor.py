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

        tcp_fx = clamp(self.tcp_force[0], p.force_min, p.force_max)

        # Create a deadband
        if abs(tcp_fx - 0) < 0.4:
            tcp_fx = 0.0

        # control law
        vx = p.gain_linear_x * tcp_fx
        wz = angular_z_ema.update(self.tcp_force[1] * p.gain_angular_z)
        # print(f"pre: {vx}")
        vx = clamp(vx, p.vel_min_x, p.vel_max_x)
        wz = clamp(wz, p.vel_min_z, p.vel_max_z)
        # print(f"post: {vx}")
        current_twist.linear.x = vx
        current_twist.angular.z = wz

        if vx != 0.0:
            print("Linear X After Limit: ", current_twist.linear.x)
        # if wz != 0.0:
        #     self.zero_vels_count = 0

        # print(f"Current Twist: {current_twist}")
        self.twist_publisher.publish(current_twist)


def main(args=None):
    rclpy.init(args=args)

    arm_service = ArmService()

    rclpy.spin(arm_service)

    arm_service.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

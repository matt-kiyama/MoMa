import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist

from tm_msgs.msg import FeedbackState
from tm_msgs.msg import StaResponse

from dataclasses import dataclass
import numpy as np

import csv
import os


@dataclass
class StiffArmParams:
    """Parameters for the stiff-arm control behavior."""

    force_max: float = 60.0  # newtons
    force_min: float = -80.0  # newtons
    vel_max_z: float = 0.030  # m/s
    vel_min_z: float = -0.030  # m/s
    vel_max_x: float = 0.040  # m/s
    vel_min_x: float = -0.060  # m/s
    gain_linear_x: float = 0.18
    gain_angular_z: float = 1.8

    # NEW: acceleration limits
    acc_limit_x: float = 0.2      # m/s^2
    acc_limit_z: float = 0.3       # rad/s^2

    # NEW: virtual damping
    damping_linear_x: float = 7.0     # N / (m/s)
    damping_angular_z: float = 3.0    # N / (rad/s)


def clamp(value: float, lower: float, upper: float) -> float:
    """Clamp a value between lower and upper bounds."""
    # print(value, lower, upper)

    return max(min(value, upper), lower)


class ArmService(Node):

    def __init__(self):
        super().__init__("arm_service")

        # -----------------------------
        # CSV logging setup
        # -----------------------------
        log_dir = os.path.expanduser("~/stiff_arm_logs")
        os.makedirs(log_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = os.path.join(
            log_dir,
            f"stiff_arm_log_{timestamp}.csv"
        )
        self.csv_file = open(log_path, mode="w", newline="")
        self.csv_writer = csv.writer(self.csv_file)

        self.csv_writer.writerow([
            "time_sec",
            "tcp_fx",
            "prev_vx",
            "damped_fx",
            "vx_des",
            "vx_cmd",
            "acc_limit_x",
            "reversing_x"
        ])

        self.start_time = self.get_clock().now()

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

        # -----------------------------
        # Time step
        # -----------------------------
        now = self.get_clock().now()
        dt = (now - self.prev_time).nanoseconds * 1e-9
        self.prev_time = now

        if dt <= 0.0 or dt > 0.1:
            dt = 0.01

        print("\n--- Stiff Arm Control Cycle ---")
        print("dt:", dt)

        # -----------------------------
        # Force input
        # -----------------------------
        tcp_fx = clamp(self.tcp_force[0], p.force_min, p.force_max)
        tcp_fy = clamp(self.tcp_force[1], p.force_min, p.force_max)

        # Deadband
        if abs(tcp_fx) < 0.4:
            tcp_fx = 0.0
        if abs(tcp_fy) < 0.4:
            tcp_fy = 0.0

        print("TCP Force (x, y):", tcp_fx, tcp_fy)
        print("Previous velocities (vx, wz):", self.prev_vx, self.prev_wz)

        # -----------------------------
        # Virtual damping (direction-aware)
        # -----------------------------
        if tcp_fx * self.prev_vx > 0.0:
            damped_fx = tcp_fx - p.damping_linear_x * self.prev_vx
            damping_x_active = True
        else:
            damped_fx = tcp_fx
            damping_x_active = False

        if tcp_fy * self.prev_wz > 0.0:
            damped_fy = tcp_fy - p.damping_angular_z * self.prev_wz
            damping_z_active = True
        else:
            damped_fy = tcp_fy
            damping_z_active = False

        print(
            "Damped Force (x, y):",
            damped_fx, damped_fy,
            "| damping active (x, z):",
            damping_x_active, damping_z_active
        )

        # -----------------------------
        # Force → desired velocity
        # -----------------------------
        vx_des = damped_fx * p.gain_linear_x
        wz_des = damped_fy * p.gain_angular_z

        print("Desired velocities (vx_des, wz_des):", vx_des, wz_des)

        # -----------------------------
        # Asymmetric acceleration limiting
        # -----------------------------
        acc_limit_x = p.acc_limit_x
        acc_limit_z = p.acc_limit_z

        reversing_x = tcp_fx * self.prev_vx < 0.0

        reversing_z = wz_des * self.prev_wz < 0.0

        if reversing_x:
            acc_limit_x *= 4.0
        if reversing_z:
            acc_limit_z *= 2.5

        print(
            "Accel limits (x, z):",
            acc_limit_x, acc_limit_z,
            "| reversing (x, z):",
            reversing_x, reversing_z
        )

        vx = self.limit_rate(
            desired=vx_des,
            previous=self.prev_vx,
            rate_limit=acc_limit_x,
            dt=dt
        )

        wz = self.limit_rate(
            desired=wz_des,
            previous=self.prev_wz,
            rate_limit=acc_limit_z,
            dt=dt
        )

        print("Rate-limited velocities (vx, wz):", vx, wz)

        # -----------------------------
        # Velocity limits
        # -----------------------------
        vx = clamp(vx, p.vel_min_x, p.vel_max_x)
        wz = clamp(wz, p.vel_min_z, p.vel_max_z)

        print("Clamped velocities (vx, wz):", vx, wz)

        # -----------------------------
        # CSV logging (offline tuning)
        # -----------------------------
        t = (now - self.start_time).nanoseconds * 1e-9

        self.csv_writer.writerow([
            t,
            tcp_fx,
            self.prev_vx,
            damped_fx,
            vx_des,
            vx,
            acc_limit_x,
            reversing_x
        ])

        # -----------------------------
        # Save state
        # -----------------------------
        self.prev_vx = vx
        self.prev_wz = wz

        # -----------------------------
        # Publish
        # -----------------------------
        current_twist.linear.x = vx
        # current_twist.angular.z = wz
        self.twist_publisher.publish(current_twist)


def main(args=None):
    rclpy.init(args=args)

    arm_service = ArmService()

    rclpy.spin(arm_service)
    arm_service.csv_file.close()

    arm_service.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

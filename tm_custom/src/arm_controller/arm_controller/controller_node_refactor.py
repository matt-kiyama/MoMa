import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist

from tm_msgs.msg import FeedbackState
from tm_msgs.msg import StaResponse

from dataclasses import dataclass
import numpy as np

import csv
import os
import datetime


@dataclass
class StiffArmParams:
    """Parameters for the stiff-arm control behavior."""

    force_max: float = 60.0  # newtons
    force_min: float = -80.0  # newtons
    vel_max_z: float = 0.030  # m/s
    vel_min_z: float = -0.030  # m/s
    vel_max_x: float = 0.040  # m/s
    vel_min_x: float = -0.040  # m/s
    gain_linear_x: float = 0.18
    gain_angular_z: float = 1.8

    # NEW: acceleration limits
    acc_limit_x = 0.3      # m/s^2
    dec_limit_x = 0.072     # m/s^2
    reversal_limit = 0.30

    acc_limit_z: float = 0.3       # rad/s^2

    # NEW: virtual damping
    damping_linear_x: float =  0.12    # N / (m/s)
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
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
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

        # -------------------------------------------------
        # Time step
        # -------------------------------------------------
        now = self.get_clock().now()
        dt = (now - self.prev_time).nanoseconds * 1e-9
        self.prev_time = now

        if dt <= 0.0 or dt > 0.1:
            dt = 0.01

        print("\n--- Stiff Arm Control Cycle ---")
        print("dt:", dt)

        # -------------------------------------------------
        # Force input
        # -------------------------------------------------
        tcp_fx = clamp(self.tcp_force[0], p.force_min, p.force_max)

        # Deadband to prevent drift
        if abs(tcp_fx) < 0.4:
            tcp_fx = 0.0

        print("TCP Force:", tcp_fx)
        print("Previous velocity:", self.prev_vx)

        # -------------------------------------------------
        # Proper admittance control
        # v = gain * force − damping * velocity
        # -------------------------------------------------
        vx_force = p.gain_linear_x * tcp_fx
        vx_damping = p.damping_linear_x * self.prev_vx

        vx_des = vx_force - vx_damping

        print("Force contribution:", vx_force)
        print("Damping contribution:", vx_damping)
        print("Desired velocity:", vx_des)

        # -------------------------------------------------
        # Separate accel / decel / reversal limits
        # -------------------------------------------------
        reversing_x = tcp_fx * self.prev_vx < 0.0

        acc_limit_x = p.acc_limit_x
        dec_limit_x = p.acc_limit_x * 0.4
        reverse_boost = 2.5

        if reversing_x:
            rate_limit_x = acc_limit_x * reverse_boost
            limit_type = "REVERSAL"

        elif abs(vx_des) < abs(self.prev_vx):
            rate_limit_x = dec_limit_x
            limit_type = "DECEL"

        else:
            rate_limit_x = acc_limit_x
            limit_type = "ACCEL"

        print("Limit type:", limit_type)
        print("Rate limit:", rate_limit_x)

        # -------------------------------------------------
        # Apply rate limiting
        # -------------------------------------------------
        vx = self.limit_rate(
            desired=vx_des,
            previous=self.prev_vx,
            rate_limit=rate_limit_x,
            dt=dt
        )

        print("Rate-limited velocity:", vx)

        # -------------------------------------------------
        # Velocity clamp
        # -------------------------------------------------
        vx = clamp(vx, p.vel_min_x, p.vel_max_x)

        print("Clamped velocity:", vx)

        # -------------------------------------------------
        # Velocity deadband (removes micro-shudder near stop)
        # -------------------------------------------------
        if abs(vx) < 0.0005:
            vx = 0.0
            print("Velocity deadband applied")

        # -------------------------------------------------
        # CSV logging
        # -------------------------------------------------
        t = (now - self.start_time).nanoseconds * 1e-9

        self.csv_writer.writerow([
            t,
            tcp_fx,
            self.prev_vx,
            vx_force,
            vx_damping,
            vx_des,
            vx,
            rate_limit_x,
            reversing_x,
            limit_type
        ])

        # Flush occasionally
        if int(t * 50) % 50 == 0:
            self.csv_file.flush()

        # -------------------------------------------------
        # Save state
        # -------------------------------------------------
        self.prev_vx = vx

        # -------------------------------------------------
        # Publish
        # -------------------------------------------------
        current_twist.linear.x = vx
        self.twist_publisher.publish(current_twist)

        print("Published velocity:", vx)


def main(args=None):
    rclpy.init(args=args)

    arm_service = ArmService()

    rclpy.spin(arm_service)
    arm_service.csv_file.close()

    arm_service.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

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

    force_max: float = 60.0          # newtons
    force_min: float = -80.0         # newtons

    vel_max_z: float = 0.050         # rad/s
    vel_min_z: float = -0.050        # rad/s
    vel_max_x: float = 0.040         # m/s
    vel_min_x: float = -0.040        # m/s

    gain_linear_x: float = 0.18
    gain_angular_z: float = 1.1

    acc_limit_x: float = 0.3         # m/s^2
    dec_limit_x: float = 0.072       # m/s^2
    reversal_limit: float = 0.30     # m/s^2 or multiplier depending on usage

    acc_limit_z: float = 0.35        # rad/s^2

    damping_linear_x: float = 0.12   # N / (m/s)
    damping_angular_z: float = 0.65   # N*m / (rad/s)

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

        self.filtered_fy = 0.0
        self.filtered_fx = 0.0

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
        tcp_fy = clamp(self.tcp_force[1], p.force_min, p.force_max)

        # Low-pass filter forces
        alpha_fx = 0.2
        alpha_fy = 0.12

        self.filtered_fx = alpha_fx * tcp_fx + (1.0 - alpha_fx) * self.filtered_fx
        self.filtered_fy = alpha_fy * tcp_fy + (1.0 - alpha_fy) * self.filtered_fy

        tcp_fx = self.filtered_fx
        tcp_fy = self.filtered_fy

        # Deadbands
        if abs(tcp_fx) < 0.4:
            tcp_fx = 0.0
        if abs(tcp_fy) < 0.6:
            tcp_fy = 0.0

        # Asymmetric soft blending
        # Keep x available, suppress z more strongly when x is active
        blend_strength_x = 0.2
        blend_strength_z = 1.4

        abs_fx = abs(tcp_fx)
        abs_fy = abs(tcp_fy)
        denom = max(abs_fx + abs_fy, 1e-6)

        fx_ratio = abs_fx / denom
        fy_ratio = abs_fy / denom

        x_scale = max(0.0, 1.0 - blend_strength_x * fy_ratio)
        z_scale = max(0.0, 1.0 - blend_strength_z * fx_ratio)

        tcp_fx = tcp_fx * x_scale
        tcp_fy = tcp_fy * z_scale

        print("TCP Force X:", tcp_fx)
        print("TCP Force Y:", tcp_fy)
        print("Blend ratios X/Y:", fx_ratio, fy_ratio)
        print("Blend scales X/Z:", x_scale, z_scale)

        # =================================================
        # ===== LINEAR X (UNCHANGED — YOUR GOOD LOGIC) =====
        # =================================================

        vx_force = p.gain_linear_x * tcp_fx
        vx_damping = p.damping_linear_x * self.prev_vx
        vx_des = vx_force - vx_damping

        reversing_x = tcp_fx * self.prev_vx < 0.0

        acc_limit_x = p.acc_limit_x
        dec_limit_x = p.acc_limit_x * 0.4
        reverse_boost = 2.5

        if reversing_x:
            rate_limit_x = acc_limit_x * reverse_boost
            limit_type_x = "REVERSAL"
        elif abs(vx_des) < abs(self.prev_vx):
            rate_limit_x = dec_limit_x
            limit_type_x = "DECEL"
        else:
            rate_limit_x = acc_limit_x
            limit_type_x = "ACCEL"

        vx = self.limit_rate(vx_des, self.prev_vx, rate_limit_x, dt)
        vx = clamp(vx, p.vel_min_x, p.vel_max_x)

        if abs(vx) < 0.0005:
            vx = 0.0

        # =================================================
        # ============ ANGULAR Z (REGENERATED) ============
        # =================================================

        wz_force = p.gain_angular_z * tcp_fy
        wz_damping = p.damping_angular_z * self.prev_wz
        wz_des = wz_force - wz_damping

        print("Z Force contribution:", wz_force)
        print("Z Damping contribution:", wz_damping)
        print("Z Desired velocity:", wz_des)

        reversing_z = tcp_fy * self.prev_wz < 0.0

        acc_limit_z = p.acc_limit_z
        dec_limit_z = p.acc_limit_z * 0.35
        reverse_boost_z = 1.5

        if reversing_z:
            rate_limit_z = acc_limit_z * reverse_boost_z
            limit_type_z = "REVERSAL"
        elif abs(wz_des) < abs(self.prev_wz):
            rate_limit_z = dec_limit_z
            limit_type_z = "DECEL"
        else:
            rate_limit_z = acc_limit_z
            limit_type_z = "ACCEL"

        print("Z Limit type:", limit_type_z)
        print("Z Rate limit:", rate_limit_z)

        wz = self.limit_rate(
            desired=wz_des,
            previous=self.prev_wz,
            rate_limit=rate_limit_z,
            dt=dt
        )

        print("Z Rate-limited velocity:", wz)

        wz_before_clamp = wz
        wz = clamp(wz, p.vel_min_z, p.vel_max_z)

        if wz != wz_before_clamp:
            print("Angular velocity clamped!")

        print("Z Clamped velocity:", wz)

        if abs(wz) < 0.0005:
            wz = 0.0
            print("Z Velocity deadband applied")

        print("Final wz:", wz)

        # -------------------------------------------------
        # CSV logging (extended)
        # -------------------------------------------------
        t = (now - self.start_time).nanoseconds * 1e-9

        self.csv_writer.writerow([
            # Time
            "time_sec",

            # -------- Linear X --------
            "tcp_fx",
            "prev_vx",
            "vx_force",
            "vx_damping",
            "vx_des",
            "vx_cmd",
            "rate_limit_x",
            "reversing_x",
            "limit_type_x",

            # -------- Angular Z --------
            "tcp_fy",
            "prev_wz",
            "wz_force",
            "wz_damping",
            "wz_des",
            "wz_cmd",
            "rate_limit_z",
            "limit_type_z"
        ])

        if int(t * 50) % 50 == 0:
            self.csv_file.flush()

        # -------------------------------------------------
        # Save state
        # -------------------------------------------------
        self.prev_vx = vx
        self.prev_wz = wz

        # -------------------------------------------------
        # Publish
        # -------------------------------------------------
        current_twist.linear.x = vx
        current_twist.angular.z = wz
        self.twist_publisher.publish(current_twist)

        print("Published vx:", vx, "| wz:", wz)



def main(args=None):
    rclpy.init(args=args)

    arm_service = ArmService()

    rclpy.spin(arm_service)
    arm_service.csv_file.close()

    arm_service.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

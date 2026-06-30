import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rcl_interfaces.msg import SetParametersResult
from rclpy.parameter import Parameter
from rclpy.qos import qos_profile_sensor_data

from tm_msgs.msg import FeedbackState
from tm_msgs.msg import StaResponse

from dataclasses import asdict, dataclass
import numpy as np

import csv
import os
import datetime


@dataclass
class StiffArmParams:
    """Parameters for the stiff-arm control behavior."""

    force_max: float = 60.0          # newtons
    force_min: float = -80.0         # newtons

    vel_max_z: float = 0.070         # rad/s
    vel_min_z: float = -0.070        # rad/s
    vel_max_x: float = 0.060         # m/s
    vel_min_x: float = -0.060        # m/s

    gain_linear_x: float = 0.18
    gain_angular_z: float = 1.1

    acc_limit_x: float = 0.3         # m/s^2
    # dec_limit_x: float = 0.072       # m/s^2
    dec_limit_x: float = 0.12      # m/s^2
    reversal_limit: float = 0.30     # m/s^2 or multiplier depending on usage

    acc_limit_z: float = 0.35        # rad/s^2

    damping_linear_x: float = 0.24   # N / (m/s)
    damping_angular_z: float = 0.65   # N*m / (rad/s)

def clamp(value: float, lower: float, upper: float) -> float:
    """Clamp a value between lower and upper bounds."""
    # print(value, lower, upper)

    return max(min(value, upper), lower)


class ArmService(Node):
    STIFF_PARAM_PREFIX = "stiff_arm"
    STIFF_PARAM_FIELDS = tuple(StiffArmParams.__dataclass_fields__.keys())

    DEFAULT_STOP_LINEAR_X_THRESHOLD = 0.03
    DEFAULT_STOP_LINEAR_Y_THRESHOLD = 0.03
    DEFAULT_STOP_ANGULAR_Z_THRESHOLD = 0.05
    DEFAULT_STOP_HOLD_TIME_SEC = 0.25

    def __init__(self):
        super().__init__("arm_service")

        # -----------------------------
        # CSV logging setup
        # -----------------------------
        log_dir = os.path.expanduser(
            os.environ.get("STIFF_ARM_LOG_DIR", "~/stiff_arm_logs")
        )
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
            "raw_tcp_fx",
            "tcp_fx",
            "prev_vx",
            "vx_force",
            "vx_damping",
            "vx_des",
            "vx_cmd",
            "rate_limit_x",
            "reversing_x",
            "limit_type_x",
            "raw_tcp_fy",
            "tcp_fy",
            "prev_wz",
            "wz_force",
            "wz_damping",
            "wz_des",
            "wz_cmd",
            "rate_limit_z",
            "limit_type_z",
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
        self.odom_topic = self.declare_parameter("odom_topic", "/platform/odometry").value
        self.stop_linear_x_threshold = abs(float(self.declare_parameter(
            "stop_linear_x_threshold",
            self.DEFAULT_STOP_LINEAR_X_THRESHOLD,
        ).value))
        self.stop_linear_y_threshold = abs(float(self.declare_parameter(
            "stop_linear_y_threshold",
            self.DEFAULT_STOP_LINEAR_Y_THRESHOLD,
        ).value))
        self.stop_angular_z_threshold = abs(float(self.declare_parameter(
            "stop_angular_z_threshold",
            self.DEFAULT_STOP_ANGULAR_Z_THRESHOLD,
        ).value))
        self.stop_hold_time_sec = max(0.0, float(self.declare_parameter(
            "stop_hold_time_sec",
            self.DEFAULT_STOP_HOLD_TIME_SEC,
        ).value))

        self.odom_subscription = self.create_subscription(
            Odometry, self.odom_topic, self.odom_callback, qos_profile_sensor_data
        )

        self.feedback_subscription
        self.sta_subscription
        self.odom_subscription

        # Publisher
        self.twist_publisher = self.create_publisher(Twist, "/platform/velocity_command", 10)

        self.cur_pos_cartesian = np.array([])
        self.tool_pose = np.array([])
        self.current_tag = 0
        self.zero_vels_count = 0
        self.sta_response_val = False

        self.base_is_stopped = False
        self._stopped_since_sec = None
        self._last_odom_sec = None
        self._last_odom_linear_x = 0.0
        self._last_odom_linear_y = 0.0
        self._last_odom_angular_z = 0.0
        self._last_odom_below_threshold = False

        self.declare_parameter("angle", 91.0)
        self._declare_stiff_arm_parameters()
        self._apply_param_values_to_struct(self._read_stiff_arm_parameter_values())
        self.param_callback_handle = self.add_on_set_parameters_callback(self._on_set_parameters)

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

    def _declare_stiff_arm_parameters(self):
        defaults = asdict(self.params)
        for field_name in self.STIFF_PARAM_FIELDS:
            self.declare_parameter(
                f"{self.STIFF_PARAM_PREFIX}.{field_name}",
                float(defaults[field_name]),
            )

    def _read_stiff_arm_parameter_values(self):
        values = {}
        for field_name in self.STIFF_PARAM_FIELDS:
            param_value = self.get_parameter(f"{self.STIFF_PARAM_PREFIX}.{field_name}").value
            values[field_name] = float(param_value)
        return values

    def _apply_param_values_to_struct(self, values):
        for field_name in self.STIFF_PARAM_FIELDS:
            setattr(self.params, field_name, float(values[field_name]))

    def _validate_stiff_arm_params(self, values):
        if values["force_min"] >= values["force_max"]:
            return False, "force_min must be less than force_max."

        if values["vel_min_x"] >= values["vel_max_x"]:
            return False, "vel_min_x must be less than vel_max_x."

        if values["vel_min_z"] >= values["vel_max_z"]:
            return False, "vel_min_z must be less than vel_max_z."

        if values["acc_limit_x"] <= 0.0:
            return False, "acc_limit_x must be > 0."

        if values["dec_limit_x"] <= 0.0:
            return False, "dec_limit_x must be > 0."

        if values["reversal_limit"] <= 0.0:
            return False, "reversal_limit must be > 0."

        if values["acc_limit_z"] <= 0.0:
            return False, "acc_limit_z must be > 0."

        if values["gain_linear_x"] < 0.0 or values["gain_angular_z"] < 0.0:
            return False, "gain values must be >= 0."

        if values["damping_linear_x"] < 0.0 or values["damping_angular_z"] < 0.0:
            return False, "damping values must be >= 0."

        return True, ""

    def _on_set_parameters(self, parameters):
        result = SetParametersResult(successful=True, reason="")

        updates = {}
        for param in parameters:
            if not param.name.startswith(f"{self.STIFF_PARAM_PREFIX}."):
                continue

            field_name = param.name.split(".", 1)[1]
            if field_name not in self.STIFF_PARAM_FIELDS:
                result.successful = False
                result.reason = f"Unknown stiff-arm parameter: {param.name}"
                return result

            if param.type_ not in (Parameter.Type.DOUBLE, Parameter.Type.INTEGER):
                result.successful = False
                result.reason = f"Parameter {param.name} must be numeric."
                return result

            updates[field_name] = float(param.value)

        if not updates:
            return result

        if not self.base_is_stopped:
            result.successful = False
            result.reason = self._base_stop_guard_reason()
            return result

        candidate_values = asdict(self.params)
        candidate_values.update(updates)

        is_valid, reason = self._validate_stiff_arm_params(candidate_values)
        if not is_valid:
            result.successful = False
            result.reason = reason
            return result

        self._apply_param_values_to_struct(candidate_values)
        return result

    def odom_callback(self, msg):
        linear_x = msg.twist.twist.linear.x
        linear_y = msg.twist.twist.linear.y
        angular_z = msg.twist.twist.angular.z

        below_threshold = (
            abs(linear_x) <= self.stop_linear_x_threshold
            and abs(linear_y) <= self.stop_linear_y_threshold
            and abs(angular_z) <= self.stop_angular_z_threshold
        )

        now_sec = self.get_clock().now().nanoseconds * 1e-9
        self._last_odom_sec = now_sec
        self._last_odom_linear_x = linear_x
        self._last_odom_linear_y = linear_y
        self._last_odom_angular_z = angular_z
        self._last_odom_below_threshold = below_threshold
        if below_threshold:
            if self._stopped_since_sec is None:
                self._stopped_since_sec = now_sec
                self.base_is_stopped = False
            else:
                self.base_is_stopped = (now_sec - self._stopped_since_sec) >= self.stop_hold_time_sec
        else:
            self._stopped_since_sec = None
            self.base_is_stopped = False

    def _base_stop_guard_reason(self):
        base_reason = (
            f"Base must be stopped for at least {self.stop_hold_time_sec:.2f}s "
            "before tuning parameters."
        )

        now_sec = self.get_clock().now().nanoseconds * 1e-9
        if self._last_odom_sec is None:
            return (
                f"{base_reason} Controller has not received odometry on "
                f"'{self.odom_topic}'."
            )

        odom_age_sec = now_sec - self._last_odom_sec
        velocity_text = (
            f"Controller odom: vx={self._last_odom_linear_x:.4f} m/s, "
            f"vy={self._last_odom_linear_y:.4f} m/s, "
            f"wz={self._last_odom_angular_z:.4f} rad/s; thresholds are "
            f"{self.stop_linear_x_threshold:.3f}, "
            f"{self.stop_linear_y_threshold:.3f}, "
            f"{self.stop_angular_z_threshold:.3f}."
        )

        if odom_age_sec > 1.0:
            return (
                f"{base_reason} Controller odometry on '{self.odom_topic}' is stale "
                f"({odom_age_sec:.2f}s old). {velocity_text}"
            )

        if self._last_odom_below_threshold and self._stopped_since_sec is not None:
            held_sec = now_sec - self._stopped_since_sec
            return (
                f"{base_reason} Controller has only seen stopped odometry for "
                f"{held_sec:.2f}s. {velocity_text}"
            )

        return f"{base_reason} {velocity_text}"


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
        raw_tcp_fx = clamp(self.tcp_force[0], p.force_min, p.force_max)
        raw_tcp_fy = clamp(self.tcp_force[1], p.force_min, p.force_max)

        # Low-pass filter forces
        alpha_fx = 0.2
        alpha_fy = 0.12
        deadband_fx = 0.4
        deadband_fy = 0.6

        # Release should not be delayed by the low-pass filter tail.
        if abs(raw_tcp_fx) < deadband_fx or raw_tcp_fx * self.filtered_fx < 0.0:
            self.filtered_fx = 0.0
        else:
            self.filtered_fx = alpha_fx * raw_tcp_fx + (1.0 - alpha_fx) * self.filtered_fx

        if abs(raw_tcp_fy) < deadband_fy or raw_tcp_fy * self.filtered_fy < 0.0:
            self.filtered_fy = 0.0
        else:
            self.filtered_fy = alpha_fy * raw_tcp_fy + (1.0 - alpha_fy) * self.filtered_fy

        tcp_fx = self.filtered_fx
        tcp_fy = self.filtered_fy

        # Deadbands after filtering suppress startup noise while raw-force reset
        # above prevents continued motion after force release.
        if abs(tcp_fx) < deadband_fx:
            tcp_fx = 0.0
        if abs(tcp_fy) < deadband_fy:
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

        print("X Force contribution:", vx_force)
        print("X Damping contribution:", vx_damping)
        print("X Desired velocity:", vx_des)

        reversing_x = tcp_fx * self.prev_vx < 0.0

        acc_limit_x = p.acc_limit_x
        dec_limit_x = p.dec_limit_x
        reverse_boost = p.reversal_limit

        if reversing_x:
            rate_limit_x = acc_limit_x * reverse_boost
            limit_type_x = "REVERSAL"
        elif abs(vx_des) < abs(self.prev_vx):
            rate_limit_x = dec_limit_x
            limit_type_x = "DECEL"
        else:
            rate_limit_x = acc_limit_x
            limit_type_x = "ACCEL"

        print("X Limit type:", limit_type_x)
        print("X Rate limit:", rate_limit_x)

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
            t,
            raw_tcp_fx,
            tcp_fx,
            self.prev_vx,
            vx_force,
            vx_damping,
            vx_des,
            vx,
            rate_limit_x,
            reversing_x,
            limit_type_x,
            raw_tcp_fy,
            tcp_fy,
            self.prev_wz,
            wz_force,
            wz_damping,
            wz_des,
            wz,
            rate_limit_z,
            limit_type_z,
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

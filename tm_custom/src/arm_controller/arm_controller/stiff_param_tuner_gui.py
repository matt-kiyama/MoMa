import tkinter as tk
from tkinter import messagebox
import time

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.parameter import Parameter, parameter_value_to_python
from rclpy.parameter_client import AsyncParameterClient
from rclpy.qos import qos_profile_sensor_data


class StiffParamTunerGui(Node):
    PARAM_PREFIX = "stiff_arm"
    PARAM_FIELDS = (
        "force_max",
        "force_min",
        "vel_max_z",
        "vel_min_z",
        "vel_max_x",
        "vel_min_x",
        "gain_linear_x",
        "gain_angular_z",
        "acc_limit_x",
        "dec_limit_x",
        "reversal_limit",
        "acc_limit_z",
        "damping_linear_x",
        "damping_angular_z",
    )
    PARAM_DESCRIPTIONS = {
        "force_max": "Upper clamp for measured TCP force (N).",
        "force_min": "Lower clamp for measured TCP force (N).",
        "vel_max_z": "Maximum commanded base angular velocity around Z (rad/s).",
        "vel_min_z": "Minimum commanded base angular velocity around Z (rad/s).",
        "vel_max_x": "Maximum commanded base linear velocity in X (m/s).",
        "vel_min_x": "Minimum commanded base linear velocity in X (m/s).",
        "gain_linear_x": "Gain from filtered force-X to desired linear velocity-X.",
        "gain_angular_z": "Gain from filtered force-Y to desired angular velocity-Z.",
        "acc_limit_x": "Rate limit for increasing linear velocity-X (m/s^2).",
        "dec_limit_x": "Rate limit for reducing linear velocity-X magnitude (m/s^2).",
        "reversal_limit": "Multiplier for X rate limit during direction reversal.",
        "acc_limit_z": "Rate limit for angular velocity-Z changes (rad/s^2).",
        "damping_linear_x": "Linear damping term applied against previous linear velocity.",
        "damping_angular_z": "Angular damping term applied against previous angular velocity.",
    }

    DEFAULT_STOP_LINEAR_X_THRESHOLD = 0.03
    DEFAULT_STOP_LINEAR_Y_THRESHOLD = 0.03
    DEFAULT_STOP_ANGULAR_Z_THRESHOLD = 0.05
    DEFAULT_STOP_HOLD_TIME_SEC = 0.25
    ODOM_STALE_TIME_SEC = 1.0

    def __init__(self, root):
        super().__init__("stiff_param_tuner_gui")
        self.root = root

        self.controller_node_name = self.declare_parameter(
            "controller_node_name",
            "arm_service",
        ).value
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

        self.param_client = AsyncParameterClient(self, self.controller_node_name)
        self.create_subscription(
            Odometry,
            self.odom_topic,
            self._odom_callback,
            qos_profile_sensor_data,
        )

        self.base_is_stopped = False
        self._stopped_since_sec = None
        self._last_odom_sec = None
        self._last_velocity_text = "waiting for odometry"
        self._controller_stop_rejected_until_sec = None
        self._controller_stop_rejected_reason = ""

        self.param_names = [f"{self.PARAM_PREFIX}.{name}" for name in self.PARAM_FIELDS]
        self.entries = {}
        self._last_loaded_values = {}
        self._pending_param_names = []
        self._updating_entries = False

        self.status_var = tk.StringVar(value="NO ODOM")
        self.velocity_status_var = tk.StringVar(value="Odom: waiting for first message.")
        self.message_var = tk.StringVar(value="Ready.")
        self._message_color = "#444444"

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._refresh_from_controller()
        self._spin_once()

    def _build_ui(self):
        self.root.title("Stiff Arm Parameter Tuner")
        self.root.geometry("980x620")

        header = tk.Frame(self.root, padx=12, pady=12)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text=f"Controller: {self.controller_node_name}",
            anchor="w",
            font=("TkDefaultFont", 10, "bold"),
        ).pack(fill=tk.X)

        status_row = tk.Frame(header)
        status_row.pack(fill=tk.X, pady=(8, 0))
        tk.Label(status_row, text="Base status:", anchor="w").pack(side=tk.LEFT)
        self.status_badge = tk.Label(
            status_row,
            textvariable=self.status_var,
            bg="#b42318",
            fg="white",
            padx=8,
            pady=2,
        )
        self.status_badge.pack(side=tk.LEFT, padx=(8, 0))
        tk.Label(
            header,
            text="Tuning is applied only when status is STOPPED.",
            anchor="w",
            fg="#666666",
            pady=4,
        ).pack(fill=tk.X)
        tk.Label(
            header,
            textvariable=self.velocity_status_var,
            anchor="w",
            fg="#666666",
            pady=2,
        ).pack(fill=tk.X)

        table_frame = tk.Frame(self.root, padx=12, pady=8)
        table_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            table_frame,
            text="Parameter",
            anchor="w",
            font=("TkDefaultFont", 9, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 6))
        tk.Label(
            table_frame,
            text="Value",
            anchor="w",
            font=("TkDefaultFont", 9, "bold"),
        ).grid(row=0, column=1, sticky="w", pady=(0, 6))
        tk.Label(
            table_frame,
            text="Description",
            anchor="w",
            font=("TkDefaultFont", 9, "bold"),
        ).grid(row=0, column=2, sticky="w", padx=(12, 0), pady=(0, 6))

        for row, field_name in enumerate(self.PARAM_FIELDS):
            display_row = row + 1
            tk.Label(
                table_frame,
                text=field_name,
                anchor="w",
                width=22,
            ).grid(row=display_row, column=0, sticky="w", padx=(0, 10), pady=3)

            entry = tk.Entry(table_frame, width=20)
            entry.grid(row=display_row, column=1, sticky="w", pady=3)
            entry.bind("<KeyRelease>", lambda _event, name=field_name: self._mark_dirty(name))
            entry.bind("<FocusOut>", lambda _event, name=field_name: self._mark_dirty(name))
            entry.bind("<Return>", lambda _event: self._apply_to_controller())
            self.entries[field_name] = entry

            tk.Label(
                table_frame,
                text=self.PARAM_DESCRIPTIONS[field_name],
                anchor="w",
                justify=tk.LEFT,
                wraplength=520,
                fg="#444444",
            ).grid(row=display_row, column=2, sticky="w", padx=(12, 0), pady=3)

        action_frame = tk.Frame(self.root, padx=12, pady=8)
        action_frame.pack(fill=tk.X)

        self.refresh_button = tk.Button(
            action_frame,
            text="Refresh",
            command=self._refresh_from_controller,
        )
        self.refresh_button.pack(side=tk.LEFT)
        self.apply_button = tk.Button(
            action_frame,
            text="Apply Changes",
            command=self._apply_to_controller,
            state=tk.DISABLED,
            padx=12,
        )
        self.apply_button.pack(side=tk.LEFT, padx=(8, 0))

        self.message_label = tk.Label(
            self.root,
            textvariable=self.message_var,
            anchor="w",
            fg=self._message_color,
            padx=12,
            pady=8,
        )
        self.message_label.pack(fill=tk.X)

    def _odom_callback(self, msg):
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
        self._last_velocity_text = (
            f"vx={linear_x:.4f} m/s, vy={linear_y:.4f} m/s, wz={angular_z:.4f} rad/s "
            f"(stopped when <= {self.stop_linear_x_threshold:.3f}, "
            f"{self.stop_linear_y_threshold:.3f}, {self.stop_angular_z_threshold:.3f})"
        )
        if below_threshold:
            if self._stopped_since_sec is None:
                self._stopped_since_sec = now_sec
                self.base_is_stopped = False
            else:
                self.base_is_stopped = (now_sec - self._stopped_since_sec) >= self.stop_hold_time_sec
        else:
            self._stopped_since_sec = None
            self.base_is_stopped = False

    def _refresh_status_badge(self):
        now_sec = self.get_clock().now().nanoseconds * 1e-9
        if (
            self._controller_stop_rejected_until_sec is not None
            and now_sec < self._controller_stop_rejected_until_sec
        ):
            self.status_var.set("CTRL NOT STOPPED")
            self.status_badge.configure(bg="#b42318")
            self.velocity_status_var.set(f"Controller says: {self._controller_stop_rejected_reason}")
        elif self._last_odom_sec is None:
            self.status_var.set("NO ODOM")
            self.status_badge.configure(bg="#6b7280")
            self.velocity_status_var.set(f"Odom topic '{self.odom_topic}': waiting for first message.")
        elif (now_sec - self._last_odom_sec) > self.ODOM_STALE_TIME_SEC:
            self.status_var.set("ODOM STALE")
            self.status_badge.configure(bg="#9a6700")
            self.velocity_status_var.set(f"Odom topic '{self.odom_topic}' has not updated recently.")
        elif self.base_is_stopped:
            self.status_var.set("STOPPED")
            self.status_badge.configure(bg="#18794e")
            self.velocity_status_var.set(f"Odom: {self._last_velocity_text}")
        else:
            self.status_var.set("MOVING")
            self.status_badge.configure(bg="#b42318")
            self.velocity_status_var.set(f"Odom: {self._last_velocity_text}")

    def _refresh_from_controller(self):
        if not self.param_client.wait_for_services(timeout_sec=1.0):
            self.message_var.set("Controller parameter service is unavailable.")
            return

        future = self.param_client.get_parameters(self.param_names)
        future.add_done_callback(self._handle_refresh_result)
        self.message_var.set("Refreshing parameter values...")

    def _handle_refresh_result(self, future):
        try:
            values = self._response_items(future.result(), "values")
        except Exception as exc:  # pylint: disable=broad-except
            self.root.after(
                0,
                lambda: self.message_var.set(f"Failed to read parameters: {exc}"),
            )
            return

        def update_entries():
            self._updating_entries = True
            for param_name, param_value in zip(self.param_names, values):
                field_name = param_name.split(".", 1)[1]
                value = parameter_value_to_python(param_value)
                formatted_value = f"{float(value):.6g}"
                entry = self.entries[field_name]
                entry.delete(0, tk.END)
                entry.insert(0, formatted_value)
                self._last_loaded_values[field_name] = formatted_value
            self._updating_entries = False
            self._set_apply_enabled(False)
            self._set_message("Parameters refreshed.", "#444444")

        self.root.after(0, update_entries)

    def _apply_to_controller(self):
        if not self.param_client.wait_for_services(timeout_sec=1.0):
            self._set_message("Controller parameter service is unavailable.", "#b42318")
            return

        params_to_send = []
        pending_param_names = []
        for field_name, entry in self.entries.items():
            raw_text = entry.get().strip()
            if raw_text == self._last_loaded_values.get(field_name):
                continue

            try:
                value = float(raw_text)
            except ValueError:
                messagebox.showerror("Invalid value", f"{field_name} must be a number.")
                return

            param_name = f"{self.PARAM_PREFIX}.{field_name}"
            params_to_send.append(Parameter(param_name, value=value))
            pending_param_names.append(param_name)

        if not params_to_send:
            self._set_message("No unapplied tuning changes.", "#444444")
            self._set_apply_enabled(False)
            return

        self._pending_param_names = pending_param_names
        future = self.param_client.set_parameters(params_to_send)
        future.add_done_callback(self._handle_apply_result)
        self._set_apply_enabled(False)
        self._set_message(f"Applying {len(params_to_send)} tuning change(s)...", "#444444")

    def _handle_apply_result(self, future):
        try:
            results = self._response_items(future.result(), "results")
        except Exception as exc:  # pylint: disable=broad-except
            self.root.after(
                0,
                lambda: self.message_var.set(f"Parameter apply failed: {exc}"),
            )
            return

        rejected_reasons = [result.reason for result in results if not result.successful]
        successful_count = sum(1 for result in results if result.successful)

        def update_ui():
            if rejected_reasons:
                reason_text = "\n".join(reason for reason in rejected_reasons if reason)
                if not reason_text:
                    reason_text = "Controller rejected one or more parameters."
                if "Base must be stopped" in reason_text:
                    self._show_controller_stop_rejection(reason_text)
                messagebox.showwarning("Apply rejected", reason_text)
                self._set_message("Apply rejected by controller.", "#b42318")
                self._set_apply_enabled(True)
                self._refresh_from_controller()
            else:
                timestamp = time.strftime("%H:%M:%S")
                self._remember_current_entry_values()
                self._set_apply_enabled(False)
                self._set_message(
                    f"Applied {successful_count} tuning change(s) at {timestamp}.",
                    "#18794e",
                )

        self.root.after(0, update_ui)

    @staticmethod
    def _response_items(response, field_name):
        return getattr(response, field_name, response)

    def _mark_dirty(self, _field_name):
        if self._updating_entries:
            return

        dirty_fields = [
            field_name
            for field_name, entry in self.entries.items()
            if entry.get().strip() != self._last_loaded_values.get(field_name)
        ]
        self._set_apply_enabled(bool(dirty_fields))
        if dirty_fields:
            self._set_message(
                f"{len(dirty_fields)} unapplied tuning change(s). Click Apply Changes.",
                "#9a6700",
            )
        else:
            self._set_message("No unapplied tuning changes.", "#444444")

    def _remember_current_entry_values(self):
        for field_name, entry in self.entries.items():
            self._last_loaded_values[field_name] = entry.get().strip()

    def _set_apply_enabled(self, enabled):
        self.apply_button.configure(state=tk.NORMAL if enabled else tk.DISABLED)

    def _set_message(self, text, color):
        self.message_var.set(text)
        self._message_color = color
        if hasattr(self, "message_label"):
            self.message_label.configure(fg=color)

    def _show_controller_stop_rejection(self, reason_text):
        now_sec = self.get_clock().now().nanoseconds * 1e-9
        self._controller_stop_rejected_until_sec = now_sec + 5.0
        self._controller_stop_rejected_reason = reason_text

    def _spin_once(self):
        if not rclpy.ok():
            return

        rclpy.spin_once(self, timeout_sec=0.01)
        self._refresh_status_badge()
        self.root.after(50, self._spin_once)

    def _on_close(self):
        self.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        self.root.destroy()


def main(args=None):
    rclpy.init(args=args)
    root = tk.Tk()
    StiffParamTunerGui(root)
    root.mainloop()


if __name__ == "__main__":
    main()

import os
from types import SimpleNamespace

import pytest
import rclpy
from nav_msgs.msg import Odometry
from rclpy.duration import Duration
from rclpy.parameter import Parameter
import numpy as np

from arm_controller.controller_node_refactor import ArmService
from arm_controller.stiff_param_tuner_gui import StiffParamTunerGui


@pytest.fixture(scope="module", autouse=True)
def rclpy_context():
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture
def arm_service_node():
    os.environ.setdefault("STIFF_ARM_LOG_DIR", "/tmp/stiff_arm_logs")
    node = ArmService()
    yield node
    node.csv_file.close()
    node.destroy_node()


def test_accepts_stiff_param_update_when_base_stopped(arm_service_node):
    arm_service_node.base_is_stopped = True
    results = arm_service_node.set_parameters(
        [
            Parameter("stiff_arm.gain_linear_x", value=0.25),
            Parameter("stiff_arm.dec_limit_x", value=0.08),
        ]
    )

    assert all(result.successful for result in results)
    assert arm_service_node.params.gain_linear_x == pytest.approx(0.25)
    assert arm_service_node.params.dec_limit_x == pytest.approx(0.08)


def test_rejects_stiff_param_update_when_base_moving(arm_service_node):
    arm_service_node.base_is_stopped = False
    previous_gain = arm_service_node.params.gain_linear_x

    results = arm_service_node.set_parameters(
        [Parameter("stiff_arm.gain_linear_x", value=0.33)]
    )

    assert len(results) == 1
    assert not results[0].successful
    assert "Base must be stopped" in results[0].reason
    assert arm_service_node.params.gain_linear_x == pytest.approx(previous_gain)
    assert "Controller has not received odometry" in results[0].reason


def test_rejects_invalid_stiff_param_ranges(arm_service_node):
    arm_service_node.base_is_stopped = True
    previous_vel_min_x = arm_service_node.params.vel_min_x

    results = arm_service_node.set_parameters(
        [Parameter("stiff_arm.vel_min_x", value=0.2)]
    )

    assert len(results) == 1
    assert not results[0].successful
    assert "vel_min_x must be less than vel_max_x" in results[0].reason
    assert arm_service_node.params.vel_min_x == pytest.approx(previous_vel_min_x)


def test_idle_odometry_noise_is_treated_as_stopped(arm_service_node):
    msg = Odometry()
    msg.twist.twist.linear.x = 0.02
    msg.twist.twist.linear.y = -0.02
    msg.twist.twist.angular.z = 0.04

    now_sec = arm_service_node.get_clock().now().nanoseconds * 1e-9
    arm_service_node._stopped_since_sec = now_sec - arm_service_node.stop_hold_time_sec
    arm_service_node.odom_callback(msg)

    assert arm_service_node.base_is_stopped


def test_reject_reason_reports_short_stop_hold_time(arm_service_node):
    msg = Odometry()
    msg.twist.twist.linear.x = 0.0
    msg.twist.twist.linear.y = 0.0
    msg.twist.twist.angular.z = 0.0

    arm_service_node.odom_callback(msg)
    results = arm_service_node.set_parameters(
        [Parameter("stiff_arm.gain_linear_x", value=0.33)]
    )

    assert len(results) == 1
    assert not results[0].successful
    assert "only seen stopped odometry" in results[0].reason
    assert "Controller odom" in results[0].reason


def test_odometry_above_stop_threshold_is_moving(arm_service_node):
    msg = Odometry()
    msg.twist.twist.linear.x = arm_service_node.stop_linear_x_threshold + 0.001

    arm_service_node.base_is_stopped = True
    arm_service_node._stopped_since_sec = (
        arm_service_node.get_clock().now().nanoseconds * 1e-9
        - arm_service_node.stop_hold_time_sec
    )
    arm_service_node.odom_callback(msg)

    assert not arm_service_node.base_is_stopped
    assert arm_service_node._stopped_since_sec is None


def test_x_filter_resets_on_force_release(arm_service_node):
    arm_service_node.filtered_fx = 5.0
    arm_service_node.prev_vx = 0.04
    arm_service_node.prev_time = arm_service_node.get_clock().now() - Duration(seconds=0.02)
    arm_service_node.tcp_force = np.array([0.0, 0.0])

    arm_service_node._stiff_arm_control()

    assert arm_service_node.filtered_fx == pytest.approx(0.0)
    assert arm_service_node.prev_vx < 0.04


def test_gui_extracts_parameter_client_response_items():
    direct_items = ["a", "b"]
    wrapped_items = SimpleNamespace(values=["c", "d"], results=["e", "f"])

    assert StiffParamTunerGui._response_items(direct_items, "values") == direct_items
    assert StiffParamTunerGui._response_items(wrapped_items, "values") == ["c", "d"]
    assert StiffParamTunerGui._response_items(wrapped_items, "results") == ["e", "f"]

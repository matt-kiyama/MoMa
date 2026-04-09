import pytest
import rclpy
from rclpy.parameter import Parameter

from arm_controller.controller_node_refactor import ArmService


@pytest.fixture(scope="module", autouse=True)
def rclpy_context():
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture
def arm_service_node():
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

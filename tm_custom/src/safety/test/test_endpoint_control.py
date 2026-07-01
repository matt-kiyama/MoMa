import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safety.endpoint_control import (
    ArmWorkspace,
    AxisLimits,
    BaseVelocityLimits,
    EndpointControlConfig,
    EndpointControlLaw,
    EndpointRobotState,
)


def make_law():
    return EndpointControlLaw(
        EndpointControlConfig(
            arm_workspace=ArmWorkspace(
                x=AxisLimits(250.0, 700.0),
                y=AxisLimits(-300.0, 200.0),
                z=AxisLimits(150.0, 800.0),
            ),
            base_velocity_limits=BaseVelocityLimits(linear_x_min=-1.5, linear_x_max=0.5),
        )
    )


def test_reachable_goal_uses_arm_without_base_motion():
    law = make_law()
    state = EndpointRobotState(
        base_position_mm=(0.0, 0.0, 0.0),
        arm_tcp_position_mm=(400.0, 0.0, 200.0),
    )

    command = law.compute(state, (704.8, 0.0, 587.35))

    assert command.arm_target_mm == pytest.approx((400.0, 0.0, 200.0))
    assert command.base_linear_x_mps == 0.0
    assert command.at_goal


def test_far_x_goal_extends_arm_and_moves_base_through_safety_topic():
    law = make_law()
    state = EndpointRobotState(
        base_position_mm=(0.0, 0.0, 0.0),
        arm_tcp_position_mm=(300.0, 0.0, 200.0),
    )

    command = law.compute(state, (1304.8, 0.0, 587.35))

    assert command.arm_target_mm[0] == 680.0
    assert command.base_linear_x_mps > 0.0
    assert command.base_linear_x_mps <= 0.5
    assert "x" in command.clamped_axes

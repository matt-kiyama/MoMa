from dataclasses import dataclass, field
from typing import Any, List
from geometry_msgs.msg import Twist

@dataclass
class Mobile_Manipulator_Arm_Offsets:
    x_in: float = 12.0
    x_mm: float = 304.8 
    y_in: float = 0.0
    y_mm: float = 0.0
    z_in: float = 15.25
    z_mm: float = 387.35

@dataclass
class Mobile_Manipulator_Arm_Feedback:
    tm_feedback: Any

@dataclass
class Mobile_Manipulator_Arm_Thresholds:
    @dataclass
    class JointThresholds:
        joint_1_min: float
        joint_1_max: float
        joint_2_min: float
        joint_2_max: float
        joint_3_min: float
        joint_3_max: float
        joint_4_min: float
        joint_4_max: float
        joint_5_min: float
        joint_5_max: float
        joint_6_min: float
        joint_6_max: float

    @dataclass
    class XYZThresholds:
        x_min: float
        x_max: float
        y_min: float
        y_max: float
        z_min: float
        z_max: float

    @dataclass
    class VelocityThresholds:
        joint_velocity: float
        tcp_velocity: float

    joint_thresholds: JointThresholds
    xyz_thresholds: XYZThresholds
    velocity_thresholds: VelocityThresholds

@dataclass
class Mobile_Manipulator_Arm:
    Offsets: Mobile_Manipulator_Arm_Offsets
    Thresholds: Mobile_Manipulator_Arm_Thresholds
    Feedback: Mobile_Manipulator_Arm_Feedback

@dataclass
class Mobile_Manipulator_Base_Odometry:
    pos_x_mm: float = 0.0
    pos_y_mm: float = 0.0
    pos_z_mm: float = 0.0
    orientation_x = None
    orientation_y = None
    orientation_z = None
    vel_linear_x = None
    vel_linear_y = None
    vel_linear_z = None
    vel_angular_x = None
    vel_angular_y = None
    vel_angular_z = None
    error_x_mm = None

@dataclass
class Mobile_Manipulator_Base_Thresholds:
    x_linear_min: float
    x_linear_max: float
    y_linear_min: float
    y_linear_max: float
    z_linear_min: float
    z_linear_max: float
    x_angular_min: float
    x_angular_max: float
    y_angular_min: float
    y_angular_max: float
    z_angular_min: float
    z_angular_max: float

@dataclass 
class Mobile_Manipulator_Base:
    Odometry: Mobile_Manipulator_Base_Odometry
    Thresholds: Mobile_Manipulator_Base_Thresholds
    Current_Twist: Twist

@dataclass
class Mobile_Manipulator_Robot:
    Arm: Mobile_Manipulator_Arm
    Base: Mobile_Manipulator_Base
    tcp_x_mm: float
    tcp_y_mm: float
    tcp_z_mm: float
    tcp_velocity: float
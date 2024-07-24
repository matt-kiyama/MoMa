import rclpy
from rclpy.node import Node

import numpy as np 

from std_msgs.msg import Bool
from tm_msgs.msg import FeedbackState
from nav_msgs.msg import Odometry
from tm_msgs.srv import SetPositions, SetEvent
from geometry_msgs.msg import Twist

import sys 
import os
sys.path.append(os.path.abspath("/home/rslomron/MoMa/tm_custom/src/safety/safety/"))
from threshold import *
from config_loader import *
from dataclasses import dataclass, field
from typing import Any, List

path_to_arm_yaml = '/home/rslomron/MoMa/tm_custom/src/safety/safety/arm_thresholds.yaml'
path_to_base_yaml = '/home/rslomron/MoMa/tm_custom/src/safety/safety/base_thresholds.yaml'

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


def mm_to_in(mm):
    # 1 millimeter is equal to 0.0393701 inches
    inches = mm * 0.0393701
    return inches

class SafetyNode(Node):

    def __init__(self):
        super().__init__('safety_node')

        #ARM
        self.arm_offsets = Mobile_Manipulator_Arm_Offsets()
        self.arm_thresholds = load_arm_thresholds_from_yaml(path_to_arm_yaml)
        self.arm_feedback = None

        self.arm = Mobile_Manipulator_Arm(
            Offsets = self.arm_offsets,
            Thresholds = self.arm_thresholds,
            Feedback = self.arm_feedback
            )
        #safety service that arm controller will use     
        self.srv = self.create_service(SetPositions, 'safety_service', self.safety_service_callback)
        
        #client of setPositions which goes to arm
        self.set_positions_client = self.create_client(SetPositions, 'set_positions')
        
        #create client of setEvent which will be used for sending stop and clear message
        self.event_client = self.create_client(SetEvent, 'set_event')

        self.stop_and_clear_event = SetEvent.Request()
        self.stop_and_clear_event.func = SetEvent.Request.STOP

        #subscribe to FeedbackState 
        self.feedback_subscription = self.create_subscription(
            FeedbackState,
            'feedback_states',
            self.class_feedback_callback,
            10)
        self.feedback_subscription  # prevent unused variable warning


        #LD250
        self.ld250_odometry = Mobile_Manipulator_Base_Odometry()
        self.ld250_threshold = load_base_thresholds_from_yaml(path_to_base_yaml)
        
        self.ld250 = Mobile_Manipulator_Base(
            Odometry = self.ld250_odometry,
            Thresholds = self.ld250_threshold,
            Current_Twist = Twist()
        )
        
        #Publisher for velocities being sent to base
        self.ld250_cmd_vel_publisher = self.create_publisher(
            Twist,
            'ld250_cmd_vel',
            10
        )

        self.LD250_safety_vel_subscription = self.create_subscription(
            Twist,
            'ld250_safety_cmd_vel',
            self.safety_cmd_vel_callback,
            10)
        self.LD250_safety_vel_subscription  # prevent unused variable warning

        #subscribe to Odometry topic
        self.LD250_odom_subscription = self.create_subscription(
            Odometry,
            'ld250_pose',
            self.class_odometry_callback,
            10)
        self.LD250_odom_subscription  # prevent unused variable warning
    

    def feedback_check(self, msg):
        tcp_xyz = [msg.tool_pose[0], msg.tool_pose[1], msg.tool_pose[2]]
        are_within_thresholds = self.check_joint_angles_and_tcp_position_within_thresholds(
            arm=self.arm,
            requested_angles=msg.joint_pos,
            requested_tcp_position=tcp_xyz
        )
        if are_within_thresholds == False:
            self.event_client.call_async(self.stop_and_clear_event)
        
        return

    def class_feedback_callback(self, msg):
        self.arm.Feedback = msg
        self.feedback_check(self.arm.Feedback)
        # run feedback check for the arm
        # print("Joint 2 Max: ", self.arm.Thresholds.joint_thresholds.joint_2_max)
        # print("Joint 2 Pos: ", self.arm.Feedback.joint_pos[1])
 
    def new_feedback_callback(self, msg):
        self.cur_pos_cartesian = np.asarray(msg.tool_pose)
        self.combined_x_pos = self.base_x_pos + (1000 * self.cur_pos_cartesian[0]) + self.arm_offsets.x_mm
        self.combined_y_pos = self.base_y_pos + (1000 * self.cur_pos_cartesian[1]) + self.arm_offsets.y_mm
        self.combined_z_pos = self.base_z_pos + (1000 * self.cur_pos_cartesian[2]) + self.arm_offsets.z_mm

        print("Base X: %5.2fmm, Base Y: %5.2fmm, Base Z: %5.2fmm" % (self.base_x_pos, self.base_y_pos, self.base_z_pos)) 
        print("Arm X: %5.2fmm, Arm Y: %5.2fmm, Arm Z: %5.2fmm" % (self.cur_pos_cartesian[0], self.cur_pos_cartesian[1], self.cur_pos_cartesian[2])) 
        print("Combined X: %5.2fmm, Combined Y: %5.2fmm, Combined Z: %5.2fmm" % (self.combined_x_pos, self.combined_y_pos, self.combined_z_pos)) 

        # print("Base X: %5.2fin, Base Y: %5.2fin, Base Z: %5.2fin" % (mm_to_in(self.base_x_pos), mm_to_in(self.base_y_pos), mm_to_in(self.base_z_pos))) 
        # print("Arm X: %5.2fin, Arm Y: %5.2fin, Arm Z: %5.2fin" % (mm_to_in(self.cur_pos_cartesian[0]), mm_to_in(self.cur_pos_cartesian[1]), mm_to_in(self.cur_pos_cartesian[2])))
        # print("Combined X: %5.2fin, Combined Y: %5.2fin, Combined Z: %5.2fin" % (mm_to_in(self.combined_x_pos), mm_to_in(self.combined_y_pos), mm_to_in(self.combined_z_pos))) 

    def check_joint_angles_and_tcp_position_within_thresholds(self, arm: Mobile_Manipulator_Arm, requested_angles: List[float], requested_tcp_position: List[float]) -> bool:
        if not len(requested_angles) == 6:
            raise ValueError("There must be exactly 6 requested angles")

        if not len(requested_tcp_position) == 3:
            raise ValueError("There must be exactly 3 requested TCP position values (x, y, z)")

        print("Requested angles:", requested_angles)
        print("Requested TCP position:", requested_tcp_position)

        joint_thresholds = arm.Thresholds.joint_thresholds
        xyz_thresholds = arm.Thresholds.xyz_thresholds

        # Check joint angles
        for i, (angle, min_threshold, max_threshold) in enumerate(zip(
            requested_angles,
            [joint_thresholds.joint_1_min, joint_thresholds.joint_2_min, joint_thresholds.joint_3_min, 
            joint_thresholds.joint_4_min, joint_thresholds.joint_5_min, joint_thresholds.joint_6_min],
            [joint_thresholds.joint_1_max, joint_thresholds.joint_2_max, joint_thresholds.joint_3_max,
            joint_thresholds.joint_4_max, joint_thresholds.joint_5_max, joint_thresholds.joint_6_max]
        )):
            if not (min_threshold <= angle <= max_threshold):
                print(f"Angle {i + 1} out of range: {angle} not in ({min_threshold}, {max_threshold})")
                return False

        # Check TCP position
        for i, (position, min_threshold, max_threshold) in enumerate(zip(
            requested_tcp_position,
            [xyz_thresholds.x_min, xyz_thresholds.y_min, xyz_thresholds.z_min],
            [xyz_thresholds.x_max, xyz_thresholds.y_max, xyz_thresholds.z_max]
        )):
            if not (min_threshold <= position <= max_threshold):
                axis = ['x', 'y', 'z'][i]
                print(f"TCP {axis}-position out of range: {position} not in ({min_threshold}, {max_threshold})")
                return False

        print("All angles and TCP position within range")
        return True

    def adjust_joint_angles_to_thresholds(self, arm: Mobile_Manipulator_Arm, requested_angles: List[float]) -> List[float]:
        if not len(requested_angles) == 6:
            raise ValueError("There must be exactly 6 requested angles")

        print("Requested angles", requested_angles)

        joint_thresholds = arm.Thresholds.joint_thresholds

        # add velocity and acc_time checks
        adjusted_angles = [
            max(joint_thresholds.joint_1_min, min(joint_thresholds.joint_1_max, requested_angles[0])),
            max(joint_thresholds.joint_2_min, min(joint_thresholds.joint_2_max, requested_angles[1])),
            max(joint_thresholds.joint_3_min, min(joint_thresholds.joint_3_max, requested_angles[2])),
            max(joint_thresholds.joint_4_min, min(joint_thresholds.joint_4_max, requested_angles[3])),
            max(joint_thresholds.joint_5_min, min(joint_thresholds.joint_5_max, requested_angles[4])),
            max(joint_thresholds.joint_6_min, min(joint_thresholds.joint_6_max, requested_angles[5]))
        ]

        print("Adjusted angles", adjusted_angles)
        return adjusted_angles

    def adjust_joint_velocities_to_thresholds(self, arm: Mobile_Manipulator_Arm, requested_velocity: float) -> float:
        print("Requested velocities", requested_velocity)

        joint_velocity_thresholds = arm.Thresholds.velocity_thresholds.joint_velocity
        adjusted_joint_velocity = min(joint_velocity_thresholds, requested_velocity)

        print("Adjusted joint velocity: ", adjusted_joint_velocity)
        return adjusted_joint_velocity
    
    def adjust_xyz_positions_to_thresholds(self, arm: Mobile_Manipulator_Arm, requested_positions: List[float]) -> List[float]:
        if not len(requested_positions) == 6:
            raise ValueError("There must be exactly x,y,z,rx,ry,rz")

        print("Requested Position: ", requested_positions)
        # add velocity and acc_time checks  
        xyz_thresholds = arm.Thresholds.xyz_thresholds
        adjusted_positions = [
            max(xyz_thresholds.x_min, min(xyz_thresholds.x_max, requested_positions[0])),
            max(xyz_thresholds.y_min, min(xyz_thresholds.y_max, requested_positions[1])),
            max(xyz_thresholds.z_min, min(xyz_thresholds.z_max, requested_positions[2])),
            requested_positions[3],
            requested_positions[4],
            requested_positions[5],
        ]

        print("Adjusted Position: ", adjusted_positions)
        return adjusted_positions
    
    def adjust_xyz_velocities_to_thresholds(self, arm: Mobile_Manipulator_Arm, requested_velocity: float) -> float:
        print("Requested velocities", requested_velocity)

        tcp_velocity_thresholds = arm.Thresholds.velocity_thresholds.tcp_velocity
        adjusted_tcp_velocity = min(tcp_velocity_thresholds, requested_velocity)

        print("Adjusted joint velocity: ", adjusted_tcp_velocity)
        return adjusted_tcp_velocity


    def forward_request_to_move_service(self, request):
        while not self.set_positions_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('move_service not available, waiting...')
        self.set_positions_client.call_async(request)
        self.get_logger().info('Return from forward_request_callback')


    def safety_service_callback(self, request, response):
        # Perform safety checks
        print("Entering Safety Service Callback")
        print("request.motion_type: ", request.motion_type)
        print("Request Type: ", type(request))
        match request.motion_type:
            case 1: #SetPositions.PTP_J
                print("JOINT MOVE")
                #check joint angles
                request.positions = self.adjust_joint_angles_to_thresholds(arm=self.arm, requested_angles=request.positions)
                request.velocity = self.adjust_joint_velocities_to_thresholds(arm=self.arm, requested_velocity=request.velocity)
                self.forward_request_to_move_service(request)
            case 2: #SetPositions.PTP_T
                print("TCP MOVE")
                #check tcp position
                request.positions = self.adjust_xyz_positions_to_thresholds(arm=self.arm, requested_positions=request.positions)
                request.velocity = self.adjust_xyz_velocities_to_thresholds(arm=self.arm, requested_velocity=request.velocity)
                self.forward_request_to_move_service(request)
            case _:
                print("WEIRD MOVE")
        print("Leaving Safety Service Callback")
        return response
      
    def class_odometry_callback(self, msg):
        self.ld250.Odometry.pos_x_mm = msg.pose.pose.position.x
        self.ld250.Odometry.pos_y_mm = msg.pose.pose.position.y
        self.ld250.Odometry.pos_z_mm = msg.pose.pose.position.z

        self.ld250.Odometry.orientation_x = msg.pose.pose.orientation.x
        self.ld250.Odometry.orientation_y = msg.pose.pose.orientation.y
        self.ld250.Odometry.orientation_z = msg.pose.pose.orientation.z

        self.ld250.Odometry.vel_linear_x = msg.twist.twist.linear.x
        self.ld250.Odometry.vel_linear_y = msg.twist.twist.linear.y
        self.ld250.Odometry.vel_linear_z = msg.twist.twist.linear.z

        self.ld250.Odometry.vel_angular_x = msg.twist.twist.angular.x
        self.ld250.Odometry.vel_angular_y = msg.twist.twist.angular.y
        self.ld250.Odometry.vel_angular_z = msg.twist.twist.angular.z

        print_on = False

        if (print_on):
            print(f"Position: X: {self.ld250.Odometry.pos_x_mm}, Y: {self.ld250.Odometry.pos_y_mm}, Z: {self.ld250.Odometry.pos_z_mm}\n")
            
            print(f"Orientation: X: {self.ld250.Odometry.orientation_x}, Y: {self.ld250.Odometry.orientation_y}, Z: {self.ld250.Odometry.orientation_z}\n")

            print(f"Linear Velocity: X: {self.ld250.Odometry.vel_linear_x}, Y: {self.ld250.Odometry.vel_linear_y}, Z: {self.ld250.Odometry.vel_linear_z}\n")
            
            print(f"Angular Velocity: X: {self.ld250.Odometry.vel_angular_x}, Y: {self.ld250.Odometry.vel_angular_y}, Z: {self.ld250.Odometry.vel_angular_z}\n")

    def adjust_base_velocities_to_thresholds(self, base: Mobile_Manipulator_Base, requested_velocity: float) -> float:
        print("Requested velocities", requested_velocity)

        adjusted_base_velocity = max(base.Thresholds.x_linear_min, min(base.Thresholds.x_linear_max, requested_velocity))
        
        print("adjusted base velocity: ", adjusted_base_velocity)
        return adjusted_base_velocity
    
    def adjust_base_velocities_to_thresholds(self, base: Mobile_Manipulator_Base, requested_linear_x_vel: float, requested_angular_z_vel: float) -> tuple:
        print("Requested linear x velocity:", requested_linear_x_vel)
        print("Requested angular z velocity:", requested_angular_z_vel)

        adjusted_linear_x_vel = max(base.Thresholds.x_linear_min, min(base.Thresholds.x_linear_max, requested_linear_x_vel))
        adjusted_angular_z_vel = max(base.Thresholds.z_angular_min, min(base.Thresholds.z_angular_max, requested_angular_z_vel))

        print("Adjusted linear x velocity:", adjusted_linear_x_vel)
        print("Adjusted angular z velocity:", adjusted_angular_z_vel)
        
        return adjusted_linear_x_vel, adjusted_angular_z_vel

    def safety_cmd_vel_callback(self, msg):
        requested_linear_x_vel = msg.linear.x
        requested_angular_z_vel = msg.angular.z

        adjusted_linear_x_vel, adjusted_angular_z_vel = self.adjust_base_velocities_to_thresholds(
            base=self.ld250,
            requested_linear_x_vel=requested_linear_x_vel,
            requested_angular_z_vel=requested_angular_z_vel
        )

        self.ld250.Current_Twist.linear.x = adjusted_linear_x_vel / 1000.0  # Adjusting the unit if needed
        self.ld250.Current_Twist.angular.z = adjusted_angular_z_vel / 1000.0 # Adjusting the unit if needed

        self.ld250_cmd_vel_publisher.publish(self.ld250.Current_Twist)

def main(args=None):
    rclpy.init(args=args)

    feedback_state_subscriber = SafetyNode()

    rclpy.spin(feedback_state_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    feedback_state_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
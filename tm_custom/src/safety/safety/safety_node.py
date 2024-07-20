import rclpy
from rclpy.node import Node

import numpy as np 

from std_msgs.msg import Bool
from tm_msgs.msg import FeedbackState
from nav_msgs.msg import Odometry
from tm_msgs.srv import SetPositions
import sys 
import os
sys.path.append(os.path.abspath("/home/rslomron/MoMa/tm_custom/src/safety/safety/"))
from threshold import *
from config_loader import *
from dataclasses import dataclass, field
from typing import Optional, Any

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
class Mobile_Manipulator_Arm:
    Offsets: Mobile_Manipulator_Arm_Offsets
    Thresholds: Mobile_Manipulator_Arm_Thresholds
    Feedback: Mobile_Manipulator_Arm_Feedback

@dataclass
class Mobile_Manipulator_Base_Odometry:
    pos_x_mm = 0.0
    pos_y_mm = 0.0
    pos_z_mm = 0.0
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
    Thresholds:Mobile_Manipulator_Base_Thresholds

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
        self.cli = self.create_client(SetPositions, 'set_positions')

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
            Thresholds = self.ld250_threshold
        )
        
        # print(self.ld250.Thresholds)

        #subscribe to Odometry topic
        self.LD250_odom_subscription = self.create_subscription(
            Odometry,
            'ld250_pose',
            self.class_odometry_callback,
            10)
        self.LD250_odom_subscription  # prevent unused variable warning

        
        #Safety Node Stuff
        #publish safety_lock topic that other nodes can use to see safety state of arm
        self.safety_lock_publisher = self.create_publisher(Bool, 'safety_lock', 10)

        #initialize thresholds for each joint from config file
        self.joint_thresholds = create_dict_of_tuples(path_to_arm_yaml)
        
        #initialize feedback flag
        self.feedback_valid = False
        #initialize request flag
        self.safety_request_valid = False
    
    def class_feedback_callback(self, msg):
        self.arm.Feedback = msg
        print("Joint 2 Max: ", self.arm.Thresholds.joint_2_max)
        print("Joint 2 Pos: ", self.arm.Feedback.joint_pos[1])
 
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

        
    def feedback_callback(self, msg):
        
        joint_select = 4
        self.get_logger().info(f"Joint: {joint_select+1}, Position: {msg.joint_pos[joint_select]}")
        self.get_logger().info(f"Joint: {joint_select+1}, Velocity: {msg.joint_vel[joint_select]}")
        self.get_logger().info(f"Joint: {joint_select+1}, Torque: {msg.joint_tor[joint_select]}")
        # for index, element in enumerate(msg.joint_tor):
        #     self.get_logger().info(f"Joint: {index}, Torque: {element}")

        safety_lock_msg = Bool()

        angle_check_result = check_joint_angles(self, msg.joint_pos)
        print(angle_check_result)
        if angle_check_result[1]:
            self.feedback_valid = True
            #self.get_logger().info('Valid feedback: "%s"' % self.feedback_valid)
        else:
            self.feedback_valid = False
            #self.get_logger().info('Invalid feedback: "%s"' % self.feedback_valid)

        # Publish safety lock for other nodes to see or use
        safety_lock_msg.data = self.feedback_valid
        print(safety_lock_msg.data)
        self.safety_lock_publisher.publish(safety_lock_msg)

    def safety_service_callback(self, request, response):
        # Perform safety checks
        callback_success = False
        
        match request.motion_type:
            case SetPositions.PTP_J:
                print("JOINT MOVE")
                #check joint angles
            case SetPositions.PTP_T:
                print("TCP MOVE")
                #check tcp position
            case _:
                print("WEIRD MOVE")


        if self.is_safe(request):
            self.get_logger().info('Request is safe, checking feedback')
            if self.feedback_valid:
                self.get_logger().info('Feedback is safe, forwarding to move_service')
                callback_success = True
                self.forward_request_to_move_service(request)
        else:
            self.get_logger().info('Request is not safe')
            # If request is bad, don't make request. Maybe add sending a corrected request later.
            callback_success = False
        self.get_logger().info('Return from safety_service_callback')
        return callback_success

    def is_safe(self, request):
        # Implement your safety checks here
        # Check if request is out of bounds
        angle_check_result = check_joint_angles(self, request.positions)
        if angle_check_result[1]:
            self.safety_request_valid = True
            self.get_logger().info('Valid Request: "%s"' % self.safety_request_valid)
        else:
            self.safety_request_valid = False
            self.get_logger().info('Invalid Request: "%s"' % self.safety_request_valid)
        return self.safety_request_valid
    
    def forward_request_to_move_service(self, request):
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('move_service not available, waiting...')
        future = self.cli.call_async(request)
        self.get_logger().info('Return from forward_request_callback')
        return
        rclpy.spin_until_future_complete(self, future)
        #return future.result()
    
    def odometry_callback(self, msg):
        
        #store new odometry information
        self.base_x_pos = msg.pose.pose.position.x
        self.base_y_pos = msg.pose.pose.position.y
        self.base_z_pos = msg.pose.pose.position.z

        self.base_x_orientation = msg.pose.pose.orientation.x
        self.base_y_orientation = msg.pose.pose.orientation.x
        self.base_z_orientation = msg.pose.pose.orientation.x

        self.base_x_vel_linear = msg.twist.twist.linear.x
        self.base_y_vel_linear = msg.twist.twist.linear.y
        self.base_z_vel_linear = msg.twist.twist.linear.z

        self.base_x_vel_angular = msg.twist.twist.angular.x
        self.base_y_vel_angular = msg.twist.twist.angular.y
        self.base_z_vel_angular = msg.twist.twist.angular.z

        print_on = True

        if (print_on):
            print(f"Position: X: {self.base_x_pos}, Y: {self.base_y_pos}, Z: {self.base_z_pos}\n")
            
            print(f"Orientation: X: {self.base_x_orientation}, Y: {self.base_y_orientation}, Z: {self.base_z_orientation}\n")

            print(f"Linear Velocity: X: {self.base_x_vel_linear}, Y: {self.base_y_vel_linear}, Z: {self.base_z_vel_linear}\n")
            
            print(f"Angular Velocity: X: {self.base_x_vel_angular}, Y: {self.base_y_vel_angular}, Z: {self.base_z_vel_angular}\n")
        
        check_base_speed(self, msg)
    
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
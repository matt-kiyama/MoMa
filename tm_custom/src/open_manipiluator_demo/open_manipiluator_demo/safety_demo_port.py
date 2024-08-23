import rclpy
from rclpy.node import Node

import numpy as np 
from std_msgs.msg import Bool
from open_manipulator_msgs.msg import KinematicsPose, OpenManipulatorState
from open_manipulator_msgs.srv import SetJointPosition, SetKinematicsPose
from sensor_msgs.msg import JointState
from nav_msgs.msg import Odometry
from tm_msgs.srv import SetPositions
import sys 
import os
sys.path.append(os.path.abspath("/home/rslomron/MoMa/tm_custom/src/safety/safety/"))
from threshold import *
from config_loader import *
from geometry_msgs.msg import Twist


path_to_arm_yaml = '/home/rslomron/MoMa/tm_custom/src/safety/safety/arm_thresholds.yaml'
path_to_base_yaml = '/home/rslomron/MoMa/tm_custom/src/safety/safety/base_thresholds.yaml'

arm_x_offset_in = 12.0
arm_x_offset_mm = 304.8

arm_y_offset_in = 0.0
arm_y_offset_mm = 0.0

arm_z_offset_in = 15.25
arm_z_offset_mm = 387.35

plan = 0

def mm_to_in(mm):
    # 1 millimeter is equal to 0.0393701 inches
    inches = mm * 0.0393701
    return inches

class BaseAndArmController(Node):
    def __init__(self):
        super().__init__('base_and_arm_controller')
        # Open Manipulator
        # Create joint_states subscriber
        self.joint_state_subscription = self.create_subscription(
            JointState,
            'joint_states',
            self.joint_state_callback,
            self.qos)
        self.joint_state_subscription

        # Create kinematics_pose subscriber
        self.kinematics_pose_subscription = self.create_subscription(
            KinematicsPose,
            'kinematics_pose',
            self.kinematics_pose_callback,
            self.qos)
        self.kinematics_pose_subscription

        # Create manipulator state subscriber
        self.open_manipulator_state_subscription = self.create_subscription(
            OpenManipulatorState,
            'states',
            self.open_manipulator_state_callback,
            self.qos)
        self.open_manipulator_state_subscription

        # Create Service Clients
        self.goal_joint_space = self.create_client(SetJointPosition, 'goal_joint_space_path')
        self.goal_task_space = self.create_client(SetKinematicsPose, 'goal_task_space_path')
        self.goal_joint_space_req = SetJointPosition.Request()
        self.goal_task_space_req = SetKinematicsPose.Request()


        # Target position for tcp in mm (referenced from base)
        self.declare_parameter('target_tcp_position', [1400.0, -156.0, 600.0])
        self.target_tcp_position = self.get_parameter('target_tcp_position').get_parameter_value().double_array_value

        self.target_tcp_position_delta = np.array([])
        self.delta_goal_base = np.array([])
        self.delta_goal_arm = np.array([])

        self.req = SetPositions.Request()

        self.seconds_elapsed = 0.0

        #base
        self.base_x_pos = 0.0
        self.base_y_pos = 0.0
        self.base_z_pos = 0.0
        self.base_x_orientation = None
        self.base_y_orientation = None
        self.base_z_orientation = None
        self.base_x_vel_linear = None
        self.base_y_vel_linear = None
        self.base_z_vel_linear = None
        self.base_x_vel_angular = None
        self.base_y_vel_angular = None
        self.base_z_vel_angular = None
        self.base_error_x = None

        #arm
        self.arm_range_x = 600 #mm
        self.arm_stow_range_x = 300 #mm
        self.arm_stow_z_pos_tcp = 327 #mm
        self.arm_offset_mm = np.array([arm_x_offset_mm, arm_y_offset_mm, arm_z_offset_mm])

        self.present_kinematics_pose = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.goal_kinematics_pose = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.path_time = 0.5  # second

        self.combined_x_pos = 0.0
        self.combined_y_pos = 0.0
        self.combined_z_pos = 0.0

        self.timer = self.create_timer(0.1, self.control_loop)  # 10 Hz
        self.timer = self.create_timer(1.0, self.count_time)

    def kinematics_pose_callback(self, msg):
        self.present_kinematics_pose[0] = msg.pose.position.x
        self.present_kinematics_pose[1] = msg.pose.position.y
        self.present_kinematics_pose[2] = msg.pose.position.z
        self.present_kinematics_pose[3] = msg.pose.orientation.w
        self.present_kinematics_pose[4] = msg.pose.orientation.x
        self.present_kinematics_pose[5] = msg.pose.orientation.y
        self.present_kinematics_pose[6] = msg.pose.orientation.z

    def base_feedback_callback(self, msg):
        self.base_x_pos = msg.pose.pose.position.x * 1000.0
        self.base_y_pos = msg.pose.pose.position.y
        self.base_z_pos = msg.pose.pose.position.z

        self.base_x_orientation = msg.pose.pose.orientation.x
        self.base_y_orientation = msg.pose.pose.orientation.y
        self.base_z_orientation = msg.pose.pose.orientation.z

        self.base_x_vel_linear = msg.twist.twist.linear.x
        self.base_y_vel_linear = msg.twist.twist.linear.y
        self.base_z_vel_linear = msg.twist.twist.linear.z

        self.base_x_vel_angular = msg.twist.twist.angular.x
        self.base_y_vel_angular = msg.twist.twist.angular.y
        self.base_z_vel_angular = msg.twist.twist.angular.z

    def calculate_current_combined_pos(self):
        self.combined_x_pos = self.base_x_pos + (1000 * self.present_kinematics_pose[0]) + arm_x_offset_mm
        self.combined_y_pos = self.base_y_pos + (1000 * self.present_kinematics_pose[1]) + arm_y_offset_mm
        self.combined_z_pos = self.base_z_pos + (1000 * self.present_kinematics_pose[2]) + arm_z_offset_mm

    def send_goal_task_space(self):
        self.goal_task_space_req.end_effector_name = 'gripper'
        self.goal_task_space_req.kinematics_pose.pose.position.x = self.goal_kinematics_pose[0]
        self.goal_task_space_req.kinematics_pose.pose.position.y = self.goal_kinematics_pose[1]
        self.goal_task_space_req.kinematics_pose.pose.position.z = self.goal_kinematics_pose[2]
        self.goal_task_space_req.kinematics_pose.pose.orientation.w = self.goal_kinematics_pose[3]
        self.goal_task_space_req.kinematics_pose.pose.orientation.x = self.goal_kinematics_pose[4]
        self.goal_task_space_req.kinematics_pose.pose.orientation.y = self.goal_kinematics_pose[5]
        self.goal_task_space_req.kinematics_pose.pose.orientation.z = self.goal_kinematics_pose[6]
        self.goal_task_space_req.path_time = self.path_time

        try:
            send_goal_task = self.goal_task_space.call_async(self.goal_task_space_req)
        except Exception as e:
            self.get_logger().info('Sending Goal Kinematic Pose failed %r' % (e,))

    def move_base(self):
        if self.base_feedback:
            self.current_twist.linear.x
            self.twist_publisher.publish(self.current_twist)
    
    def control_law(self):
        global plan

        gain = 0.3
        print("gain: ", gain)

        if plan == 0: #initial
            self.delta_goal_base = np.subtract(self.target_tcp_position, self.base_x_pos)
            self.delta_goal_arm = np.subtract(self.delta_goal_base, self.arm_offset_mm)
            # print("delta goal base: ", self.delta_goal_base)
            print("delta_x : ", self.delta_goal_base[0])
            # print("base_x : ", self.base_x_pos)

            # print("delta goal arm: ", self.delta_goal_arm)
            # print("arm_range_x : ", self.arm_range_x)
            
            #mm = mm - mm
            print("offset + range: ", self.arm_offset_mm + self.arm_range_x)
            self.base_setpoint = self.delta_goal_base[0] - (self.arm_range_x + arm_x_offset_mm)
            self.base_stow_setpoint = self.delta_goal_base[0] - (self.arm_stow_range_x + arm_x_offset_mm)
            print("base setpoint: ", self.base_setpoint)
            print("base stow setpoint: ", self.base_stow_setpoint)

            if self.arm_range_x > self.delta_goal_arm[0]:
                #set plan 1
                print("plan 1")
                plan = 1
            else:
                #set plan 2
                print("plan 2")
                plan = 2

        if plan == 1:
            #move only arm
            print("move only arm")
            self.target_arm_position = self.delta_goal_arm
            print("arm_offset_mm: ", self.arm_offset_mm)
            print("target arm_position", self.target_arm_position)
            self.move_arm()
        if plan == 2:
            #move base and arm
            print("move base and arm")

            print("base_x : ", self.base_x_pos)
            self.base_error_x = self.base_setpoint - self.base_x_pos
            print("base_error_x: ", self.base_error_x)

            #move arm to full extension in x
            # self.target_arm_position = [self.arm_range_x, -156.0, self.target_tcp_position[2]]
            self.target_arm_position = [self.arm_range_x, -156.0, self.target_tcp_position[2]]
            self.move_arm()
            # print("publish twist")
            print("gain * base_error_x: (m/s)", (gain * self.base_error_x) / 1000.0)

            if abs(self.base_error_x) < 20.0:
                self.current_twist.linear.x = 0.0
                plan = 3
            else:
                self.current_twist.linear.x = (gain * self.base_error_x) / 1000.0 

            # keep velocity of the base within a range
            # if self.current_twist.linear.x > vel_max:
            #     self.current_twist.linear.x = vel_max
            # elif self.current_twist.linear.x < vel_min:
            #     self.current_twist.linear.x = vel_min
            self.twist_publisher.publish(self.current_twist)

        if plan == 3:
            #move base and arm
            print("move base and arm stow")

            print("base_x : ", self.base_x_pos)

            self.base_stow_error_x = self.base_stow_setpoint - self.base_x_pos
            print("base_stow_error_x: ", self.base_stow_error_x)

            print("gain * base_error_x: (mm/s)", (gain * self.base_stow_error_x) / 1000.0)

            self.target_arm_position = [self.arm_stow_range_x, -156.0, self.arm_stow_z_pos_tcp]
            self.move_arm()

            if abs(self.base_stow_error_x) < 8.0:
                self.current_twist.linear.x = 0.0
            else:
                self.current_twist.linear.x = (gain * self.base_stow_error_x) / 1000.0 
            
            self.twist_publisher.publish(self.current_twist)

    def control_loop(self):
        self.control_law()
        # self.move_base()
        # self.move_arm()

def main(args=None):
    rclpy.init(args=args)
    controller = BaseAndArmController()
    rclpy.spin(controller)
    controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
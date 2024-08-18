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
        #client of setPositions which goes to arm
        self.cli = self.create_client(SetPositions, 'set_positions')
        # self.cli = self.create_client(SetPositions, 'safety_service')

        #Publisher for velocities being sent to base
        self.twist_publisher = self.create_publisher(
            Twist,
            'ld250_safety_cmd_vel',
            10
        )

        self.current_twist = Twist()

        # Subscribers for feedback
        #subscribe to FeedbackState 
        self.feedback_subscription = self.create_subscription(
            FeedbackState,
            'feedback_states',
            self.arm_feedback_callback,
            10)
        self.feedback_subscription  # prevent unused variable warning

        self.LD250_odom_subscription = self.create_subscription(
            Odometry,
            'ld250_pose',
            self.base_feedback_callback,
            10)
        self.LD250_odom_subscription  # prevent unused variable warning

        # self.base_feedback = None
        # self.arm_feedback = None

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
        self.cur_tcp_pos_cartesian = None
        #x_max 950
        #x_min 
        #y_max 0
        #y_min 0
        #z_max 900 
        #z_min -18
        # self.arm_range = np.array([950, 0, ])
        self.arm_range_x = 600 #mm
        self.arm_stow_range_x = 300 #mm
        self.arm_stow_z_pos_tcp = 327 #mm
        self.arm_offset_mm = np.array([arm_x_offset_mm, arm_y_offset_mm, arm_z_offset_mm])
        self.target_arm_position = np.array([])

        self.combined_x_pos = 0.0
        self.combined_y_pos = 0.0
        self.combined_z_pos = 0.0

        self.timer = self.create_timer(0.1, self.control_loop)  # 10 Hz
        self.timer = self.create_timer(1.0, self.count_time)

    def count_time(self):
        self.seconds_elapsed += 1

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

    def arm_feedback_callback(self, msg):
        self.cur_tcp_pos_cartesian = np.asarray(msg.tool_pose)

    def calculate_current_combined_pos(self):
        self.combined_x_pos = self.base_x_pos + (1000 * self.cur_pos_cartesian[0]) + arm_x_offset_mm
        self.combined_y_pos = self.base_y_pos + (1000 * self.cur_pos_cartesian[1]) + arm_y_offset_mm
        self.combined_z_pos = self.base_z_pos + (1000 * self.cur_pos_cartesian[2]) + arm_z_offset_mm

    def move_base(self):
        if self.base_feedback:
            self.current_twist.linear.x
            self.twist_publisher.publish(self.current_twist)

    def move_arm(self):
        self.req.motion_type = SetPositions.Request.PTP_T

        self.req.positions = [self.target_arm_position[0]/1000, self.target_arm_position[1]/1000, self.target_arm_position[2]/1000, 3.14, 0.0, 0.0]
        
        print(self.req.positions)

        self.req.velocity = 4.0
        self.req.acc_time = 0.1
        self.req.blend_percentage = 20
        self.req.fine_goal = False

        self.future = self.cli.call_async(self.req)
        return
    
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
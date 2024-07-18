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

        #Publisher for velocities being sent to base
        self.twist_publisher = self.create_publisher(
            Twist,
            'ld250_cmd_vel',
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
        self.arm_range_x = 400 #mm
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
        self.delta_goal_base = np.subtract(self.target_tcp_position, self.base_x_pos)
        self.delta_goal_arm = np.subtract(self.delta_goal_base, self.arm_offset_mm)
        # print("delta goal base: ", self.delta_goal_base)
        # print("delta_x : ", self.delta_goal_base[0])
        # print("base_x : ", self.base_x_pos)

        # print("delta goal arm: ", self.delta_goal_arm)
        # print("arm_range_x : ", self.arm_range_x)
        
        #mm = mm - mm
        self.base_setpoint = self.delta_goal_base[0] - self.arm_range_x
        print("base setpoint: ", self.base_setpoint)

        print("base_x : ", self.base_x_pos)
        self.base_error_x = self.base_setpoint - self.base_x_pos
        print("base_error_x: ", self.base_error_x)
        

        gain = 0.3

        # vel_max = 200.0 # mm/s
        # vel_min = -200.0 # mm/s

        if plan == 0: #initial
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

            #move arm to full extension in x
            self.target_arm_position = [self.arm_range_x, -156.0, self.target_tcp_position[2]]
            self.move_arm()
            
            
            print("gain * base_error_x: (mm/s)", gain * self.base_error_x)

            if abs(self.base_error_x) < 1.0:
                self.current_twist.linear.x = 0.0
            else:
                self.current_twist.linear.x = (gain * self.base_error_x) / 1000.0 

            # keep velocity of the base within a range
            # if self.current_twist.linear.x > vel_max:
            #     self.current_twist.linear.x = vel_max
            # elif self.current_twist.linear.x < vel_min:
            #     self.current_twist.linear.x = vel_min
            self.twist_publisher.publish(self.current_twist)


    def control_loop(self):
        self.control_law()
        # self.move_base()
        # self.move_arm()

class SafetyNode(Node):

    def __init__(self):
        super().__init__('safety_node')

        #ARM
        #safety service that arm controller will use     
        self.srv = self.create_service(SetPositions, 'safety_service', self.safety_service_callback)
        
        #client of setPositions which goes to arm
        self.cli = self.create_client(SetPositions, 'set_positions')

        #subscribe to FeedbackState 
        self.feedback_subscription = self.create_subscription(
            FeedbackState,
            'feedback_states',
            self.new_feedback_callback,
            10)
        self.feedback_subscription  # prevent unused variable warning

        #publish safety_lock topic that other nodes can use to see safety state of arm
        self.safety_lock_publisher = self.create_publisher(Bool, 'safety_lock', 10)

        #initialize thresholds for each joint from config file
        self.joint_thresholds = create_dict_of_tuples(path_to_arm_yaml)
        
        #initialize feedback flag
        self.feedback_valid = False

        #initialize request flag
        self.safety_request_valid = False

        #LD250

        self.base_thresholds = create_dict_of_tuples(path_to_base_yaml)
        print(self.base_thresholds)

        #variables to hold the odometry information reported by the LD250

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

        self.combined_x_pos = 0.0
        self.combined_y_pos = 0.0
        self.combined_z_pos = 0.0

        #subscribe to Odometry 
        self.LD250_odom_subsrciption = self.create_subscription(
            Odometry,
            'ld250_pose',
            self.odometry_callback,
            10)
        self.LD250_odom_subsrciption  # prevent unused variable warning
        
    
    def new_feedback_callback(self, msg):
        self.cur_pos_cartesian = np.asarray(msg.tool_pose)
        self.combined_x_pos = self.base_x_pos + (1000 * self.cur_pos_cartesian[0]) + arm_x_offset_mm
        self.combined_y_pos = self.base_y_pos + (1000 * self.cur_pos_cartesian[1]) + arm_y_offset_mm
        self.combined_z_pos = self.base_z_pos + (1000 * self.cur_pos_cartesian[2]) + arm_z_offset_mm

        # print("Base X: %5.2fmm, Base Y: %5.2fmm, Base Z: %5.2fmm" % (self.base_x_pos, self.base_y_pos, self.base_z_pos)) 
        # print("Arm X: %5.2fmm, Arm Y: %5.2fmm, Arm Z: %5.2fmm" % (self.cur_pos_cartesian[0], self.cur_pos_cartesian[1], self.cur_pos_cartesian[2])) 
        # print("Combined X: %5.2fmm, Combined Y: %5.2fmm, Combined Z: %5.2fmm" % (self.combined_x_pos, self.combined_y_pos, self.combined_z_pos)) 

        print("Base X: %5.2fin, Base Y: %5.2fin, Base Z: %5.2fin" % (mm_to_in(self.base_x_pos), mm_to_in(self.base_y_pos), mm_to_in(self.base_z_pos))) 
        print("Arm X: %5.2fin, Arm Y: %5.2fin, Arm Z: %5.2fin" % (mm_to_in(self.cur_pos_cartesian[0]), mm_to_in(self.cur_pos_cartesian[1]), mm_to_in(self.cur_pos_cartesian[2])))
        print("Combined X: %5.2fin, Combined Y: %5.2fin, Combined Z: %5.2fin" % (mm_to_in(self.combined_x_pos), mm_to_in(self.combined_y_pos), mm_to_in(self.combined_z_pos))) 


        
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

        print_on = False

        if (print_on):
            print(f"Position: X: {self.base_x_pos}, Y: {self.base_y_pos}, Z: {self.base_z_pos}\n")
            
            print(f"Orientation: X: {self.base_x_orientation}, Y: {self.base_y_orientation}, Z: {self.base_z_orientation}\n")

            print(f"Linear Velocity: X: {self.base_x_vel_linear}, Y: {self.base_y_vel_linear}, Z: {self.base_z_vel_linear}\n")
            
            print(f"Angular Velocity: X: {self.base_x_vel_angular}, Y: {self.base_y_vel_angular}, Z: {self.base_z_vel_angular}\n")
        
        check_base_speed(self, msg)
            

# def main(args=None):
#     rclpy.init(args=args)

#     feedback_state_subscriber = SafetyNode()

#     rclpy.spin(feedback_state_subscriber)

#     # Destroy the node explicitly
#     # (optional - otherwise it will be done automatically
#     # when the garbage collector destroys the node object)
#     feedback_state_subscriber.destroy_node()
#     rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    controller = BaseAndArmController()
    rclpy.spin(controller)
    controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
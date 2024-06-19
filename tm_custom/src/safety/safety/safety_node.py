import rclpy
from rclpy.node import Node

from std_msgs.msg import Bool
from tm_msgs.msg import FeedbackState
from nav_msgs.msg import Odometry
from tm_msgs.srv import SetPositions
import sys 
import os
sys.path.append(os.path.abspath("/home/rslomron/MoMa/tm_custom/src/safety/safety/"))
from threshold import *
from config_loader import *

path_to_yaml = '/home/rslomron/MoMa/tm_custom/src/safety/safety/arm_thresholds.yaml'

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
            self.feedback_callback,
            10)
        self.feedback_subscription  # prevent unused variable warning

        #publish safety_lock topic that other nodes can use to see safety state of arm
        self.safety_lock_publisher = self.create_publisher(Bool, 'safety_lock', 10)

        #initialize thresholds for each joint from config file
        self.joint_thresholds = create_dict_of_tuples(path_to_yaml)
        
        #initialize feedback flag
        self.feedback_valid = False

        #initialize request flag
        self.safety_request_valid = False

        #LD250

        #variables to hold the odometry information reported by the LD250
        self.base_x_pos = None
        self.base_y_pos = None
        self.base_z_pos = None
        self.base_x_orientation = None
        self.base_y_orientation = None
        self.base_z_orientation = None
        self.base_x_vel_linear = None
        self.base_y_vel_linear = None
        self.base_z_vel_linear = None
        self.base_x_vel_angular = None
        self.base_y_vel_angular = None
        self.base_z_vel_angular = None

        #subscribe to Odometry 
        self.LD250_odom_subsrciption = self.create_subscription(
            Odometry,
            'ld250_pose',
            self.odometry_callback,
            10)
        self.LD250_odom_subsrciption  # prevent unused variable warning
        
        
        
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

        print_on = True

        if (print_on):
            print(f"Position: X: {self.base_x_pos}, Y: {self.base_y_pos}, Z: {self.base_z_pos}\n")
            
            print(f"Orientation: X: {self.base_x_orientation}, Y: {self.base_y_orientation}, Z: {self.base_z_orientation}\n")

            print(f"Linear Velocity: X: {self.base_x_vel_linear}, Y: {self.base_y_vel_linear}, Z: {self.base_z_vel_linear}\n")
            
            print(f"Angular Velocity: X: {self.base_x_vel_angular}, Y: {self.base_y_vel_angular}, Z: {self.base_z_vel_angular}\n")
            

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
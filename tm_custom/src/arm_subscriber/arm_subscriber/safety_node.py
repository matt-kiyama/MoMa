import rclpy
from rclpy.node import Node

from std_msgs.msg import Bool
from tm_msgs.msg import FeedbackState
import sys 
import os
sys.path.append(os.path.abspath("/home/rslomron/MoMa/tm_custom/src/arm_subscriber/arm_subscriber/"))
from threshold import *
from config_loader import *

path_to_yaml = 'arm_thresholds.yaml'

class SafetyNode(Node):

    def __init__(self):
        super().__init__('safety_node')

        #intialize subscribers and publishers
        self.feedback_subscription = self.create_subscription(
            FeedbackState,
            'feedback_states',
            self.feedback_callback,
            10)
        self.feedback_subscription  # prevent unused variable warning
        
        self.request_subscription = self.create_subscription(
            FeedbackState,
            'feedback_states',
            self.request_callback,
            10)
        self.request_subscription  # prevent unused variable warning        

        self.request_publisher = self.create_publisher(Bool, 'safety_lock', 10)

        self.joint_thresholds = create_dict_of_tuples(path_to_yaml)
        self.feedback_valid = False

    def feedback_callback(self, msg):

        angle_check_result = check_joint_angles(self, msg)
        if angle_check_result[1]:
            self.feedback_valid = True
            self.get_logger().info('Valid feedback: "%s"' % self.feedback_valid)
        else:
            self.feedback_valid = False
            self.get_logger().info('Valid feedback: "%s"' % self.feedback_valid)
    
    # def request_callback(self, msg):
    #     if self.check_request_thresholds(msg):
    #         if self.feedback_valid:
    #             self.request_publisher.publish(msg) #will turn into a request to tm_msgs srv


    def listener_callback(self, msg):
        
        safety_lock = Bool()

        #self.get_logger().info('Tool Pose: "%s"' % msg.tool_pose)

        #call threshold functions here
        #threshold functions should set self.lock true or false
        angle_check_result = check_joint_angles(self, msg)
        self.lock = angle_check_result[1]

        safety_lock.data = self.lock
        self.publisher_.publish(safety_lock)

    
    def parse_joint_pos(self, msg):
        result_strings = []
        for index, value in enumerate(msg.joint_pos):
            result_strings.append("Joint {} Angle: {}".format(index+1, value))
        return result_strings
        
            

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
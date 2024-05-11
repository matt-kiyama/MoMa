import rclpy
from rclpy.node import Node

from std_msgs.msg import Bool
from tm_msgs.msg import FeedbackState
import sys 
import os
sys.path.append(os.path.abspath("/home/rslomron/MoMa/tm_custom/src/arm_subscriber/arm_subscriber/"))
from threshold import *


class SafetyNode(Node):

    def __init__(self):
        super().__init__('safety_node')
        self.subscription = self.create_subscription(
            FeedbackState,
            'feedback_states',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

        self.publisher_ = self.create_publisher(Bool, 'safety_lock', 10)

        self.lock = True

    def listener_callback(self, msg):
        
        safety_lock = Bool()

        #self.get_logger().info('Tool Pose: "%s"' % msg.tool_pose)
        
        joint_angle_string = self.parse_joint_pos(msg)
        self.get_logger().info('%s' % joint_angle_string)

        #call threshold functions here
        #threshold functions should set self.lock true or false
        joint_thresholds_angle(self, msg)

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
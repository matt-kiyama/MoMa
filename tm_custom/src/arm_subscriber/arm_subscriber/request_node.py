import rclpy
from rclpy.node import Node

from std_msgs.msg import Bool
from tm_msgs.msg import FeedbackState
from tm_msgs.srv import SetPositions
import sys 
import os
sys.path.append(os.path.abspath("/home/rslomron/MoMa/tm_custom/src/arm_subscriber/arm_subscriber/"))
from threshold import *


class RequestNode(Node):

    def __init__(self):
        super().__init__('request_node')
        self.subscription = self.create_subscription(
            FeedbackState,
            'feedback_states',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning


    def listener_callback(self, msg):

        #self.get_logger().info('Tool Pose: "%s"' % msg.tool_pose)
        
        joint_angle_string = self.parse_joint_pos(msg)
        self.get_logger().info('%s' % joint_angle_string)
    
        
            

def main(args=None):
    rclpy.init(args=args)

    feedback_state_subscriber = RequestNode()

    rclpy.spin(feedback_state_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    feedback_state_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
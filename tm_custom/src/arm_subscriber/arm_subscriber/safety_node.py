import rclpy
from rclpy.node import Node

from std_msgs.msg import Bool
from tm_msgs.msg import FeedbackState
from tm_msgs.srv import SetPositions
import sys 
import os
sys.path.append(os.path.abspath("/home/rslomron/MoMa/tm_custom/src/arm_subscriber/arm_subscriber/"))
from threshold import *
from config_loader import *

path_to_yaml = '/home/rslomron/MoMa/tm_custom/src/arm_subscriber/arm_subscriber/arm_thresholds.yaml'

class SafetyNode(Node):

    def __init__(self):
        super().__init__('safety_node')

        #safety service that controller will use     
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

    def feedback_callback(self, msg):
        
        safety_lock_msg = Bool()

        angle_check_result = check_joint_angles(self, msg.joint_pos)
        print(angle_check_result)
        if angle_check_result[1]:
            self.feedback_valid = True
            self.get_logger().info('Valid feedback: "%s"' % self.feedback_valid)
        else:
            self.feedback_valid = False
            self.get_logger().info('Invalid feedback: "%s"' % self.feedback_valid)

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
                move_service_response = self.forward_request_to_move_service(request)
        else:
            self.get_logger().info('Request is not safe')
            # If request is bad, don't make request. Maybe add sending a corrected request later.
            callback_success = False
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
        rclpy.spin_until_future_complete(self, future)
        return future.result()
            

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
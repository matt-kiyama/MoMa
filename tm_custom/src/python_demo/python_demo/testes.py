import rclpy
from rclpy.node import Node
import math

from tm_msgs.srv import SetPositions

import sys 
import os
sys.path.append(os.path.abspath("/home/rslomron/MoMa/tm_custom/src/safety/safety/"))
from threshold import *
# sys.path.insert(0, '/home/rslomron/MoMa/tm_custom/src/arm_subscriber/arm_subscriber/')
# from threshold import *

class ArmService(Node):

    def __init__(self):
        super().__init__('arm_service')

        self.declare_parameter('angle', 91.0)

        self.cli = self.create_client(SetPositions, 'set_positions')
        #self.cli = self.create_client(SetPositions, 'safety_service')

        while not self.cli.wait_for_service(timeout_sec=1.0):
            if(rclpy.ok()):
                self.get_logger().info('service not available, waiting again...')
                return

        self.req = SetPositions.Request()

    def send_requests(self):

        self.req.motion_type = SetPositions.Request.PTP_J
        my_param = self.get_parameter('angle').get_parameter_value().double_value

        desired_joint_positions_degrees = [10, 0, 90, 0, my_param, 10] #valid
        #desired_joint_positions_degrees = [-11, 5, 130, 20, 60, 10] #invalid
        print(desired_joint_positions_degrees)
        self.req.positions = [math.radians(angle) for angle in desired_joint_positions_degrees]

        print("self.req.positions")
        print(self.req.positions)
        #self.req.positions = [0.174533, -0.005934119, 2.46283411, -0.00872665, 1.1229448, 0.26284659]
        
        self.req.velocity = 3.5
        self.req.acc_time = 0.2
        self.req.blend_percentage = 10
        self.req.fine_goal = False

        self.future = self.cli.call_async(self.req)

def main(args=None):
    rclpy.init(args=args)

    arm_service = ArmService()
    arm_service.send_requests()
    
    while rclpy.ok():
        print('test 1')
        rclpy.spin_once(arm_service)
        print('test 1')
        if arm_service.future.done():
            print('test 1')
            try:
                response = arm_service.future.result()
            except Exception as e:
                arm_service.get_logger().info()
            else:
                arm_service.get_logger().info(
                    'Velocity: %f' % arm_service.req.velocity
                )
            break

    arm_service.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
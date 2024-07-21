import rclpy
from rclpy.node import Node

import numpy as np 

from tm_msgs.srv import SetPositions
import sys 
import os
sys.path.append(os.path.abspath("/home/rslomron/MoMa/tm_custom/src/safety/safety/"))
from threshold import *
from config_loader import *

path_to_arm_stow_yaml = '/home/rslomron/MoMa/tm_custom/src/safety/safety/arm_controller_stow_position.yaml'

class ServiceClient(Node):
    def __init__(self):
        super().__init__('set_positions_client')
        self.cli = self.create_client(SetPositions, 'set_positions')
        self.cli = self.create_client(SetPositions, 'safety_service')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting again...')
        self.req = SetPositions.Request()
        self.joint_stow_position = yaml_to_np_array(path_to_arm_stow_yaml)

    def stow_arm(self):
        self.req.motion_type = SetPositions.Request.PTP_J

        self.req.positions = [math.radians(angle) for angle in self.joint_stow_position]
        
        self.req.velocity = 1.0
        self.req.acc_time = 0.2
        self.req.blend_percentage = 10
        self.req.fine_goal = False

        self.future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()

def main(args=None):
    rclpy.init(args=args)

    client = ServiceClient()
    response = client.stow_arm()
    
    if response is not None:
        result_string = 'Result of stow_arm():  ' + str(response)
        client.get_logger().info(result_string)
    else:
        client.get_logger().info('Service call failed')

    client.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
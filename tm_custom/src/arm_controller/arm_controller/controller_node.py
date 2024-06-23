import rclpy
from rclpy.node import Node
import math
import numpy as np 

from tm_msgs.srv import SetPositions
from tm_msgs.msg import FeedbackState

import sys 
import os
sys.path.append(os.path.abspath("/home/rslomron/MoMa/tm_custom/src/safety/safety/"))
from threshold import *
# sys.path.insert(0, '/home/rslomron/MoMa/tm_custom/src/arm_subscriber/arm_subscriber/')

class ArmService(Node):

    def __init__(self):
        super().__init__('arm_service')

        #subscribe to FeedbackState 
        self.feedback_subscription = self.create_subscription(
            FeedbackState,
            'feedback_states',
            self.feedback_callback,
            10)
        self.feedback_subscription  # prevent unused variable warning

        self.declare_parameter('angle', 91.0)

        self.cli = self.create_client(SetPositions, 'set_positions')
        #self.cli = self.create_client(SetPositions, 'safety_service')

        while not self.cli.wait_for_service(timeout_sec=1.0):
            if(rclpy.ok()):
                self.get_logger().info('service not available, waiting again...')
                return

        self.req = SetPositions.Request()

        
        self.cur_pos = []
        self.cur_torques = []
        self.previous_torques = []
        self.k = 0.1

    def send_requests(self):

        self.req.motion_type = SetPositions.Request.PTP_J
        my_param = self.get_parameter('angle').get_parameter_value().double_value

        print(f"self.cur_pos {self.cur_pos}")
        print(f"self.cur_torques {self.cur_torques[4]}")
        print(f"self.cur_torques {type(self.cur_torques)}")

        desired_joint_positions_degrees = [10, 0, 90, 0, self.control_law(4), 10] #valid
        #desired_joint_positions_degrees = [-11, 5, 130, 20, 60, 10] #invalid
        print(desired_joint_positions_degrees)
        self.req.positions = [math.radians(angle) for angle in desired_joint_positions_degrees]

        # print("self.req.positions")
        # print(self.req.positions)
        # self.req.positions = [0.174533, -0.005934119, 2.46283411, -0.00872665, 1.1229448, 0.26284659]
        
        self.req.velocity = 3.5
        self.req.acc_time = 0.2
        self.req.blend_percentage = 10
        self.req.fine_goal = False

        self.future = self.cli.call_async(self.req)
            
    def control_law(self, joint):
        torque_dif = self.cur_torques[joint] - self.previous_torques[joint]
        position_des = self.cur_pos[joint] + self.k * (torque_dif)
        # print(position_des)
        print(torque_dif)
        return position_des if abs(torque_dif) > 0.05 else self.cur_pos[joint]

    def feedback_callback(self, msg):
        self.cur_pos = [math.degrees(angle) for angle in msg.joint_pos]
        self.cur_torques = list(msg.joint_tor)
        if(not(self.previous_torques)):
            self.previous_torques = self.cur_torques
        self.send_requests()
        self.previous_torques = self.cur_torques
        

def main(args=None):
    rclpy.init(args=args)

    arm_service = ArmService()
    rclpy.spin(arm_service)

    # arm_service.send_requests()
    
    # while rclpy.ok():
    #     print('test 1')
    #     rclpy.spin_once(arm_service)
    #     print('test 1')
    #     if arm_service.future.done():
    #         print('test 1')
    #         try:
    #             response = arm_service.future.result()
    #         except Exception as e:
    #             arm_service.get_logger().info()
    #         else:
    #             arm_service.get_logger().info(
    #                 'Velocity: %f' % arm_service.req.velocity
    #             )
    #         break

    arm_service.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
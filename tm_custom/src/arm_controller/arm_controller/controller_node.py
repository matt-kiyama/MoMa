import rclpy
from rclpy.node import Node
import math
import numpy as np 
import time

from geometry_msgs.msg import Twist

from tm_msgs.srv import SetPositions
from tm_msgs.srv import SetEvent
from tm_msgs.msg import FeedbackState
from tm_msgs.msg import SctResponse
from tm_msgs.msg import StaResponse
from tm_msgs.srv import AskSta

import sys 
import os
sys.path.append(os.path.abspath("/home/rslomron/MoMa/tm_custom/src/safety/safety/"))
from threshold import *
# sys.path.insert(0, '/home/rslomron/MoMa/tm_custom/src/arm_subscriber/arm_subscriber/')

def map_range(x, x_min, x_max, y_min, y_max):
        m = (y_max - y_min) / (x_max - x_min)
        b = y_min - m * x_min
        return m * x + b


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

        self.sta_subscription = self.create_subscription(
            StaResponse,
            'sta_response',
            self.sta_callback,
            10)
        self.sta_subscription  # prevent unused variable warning

        self.twist_publisher = self.create_publisher(
            Twist,
            'ld250_cmd_vel',
            10
        )

        self.current_twist = Twist()

            #subscribe to SctResponse 
        # self.sct_subscription = self.create_subscription(
        #     SctResponse,
        #     'sct_response',
        #     self.sct_callback,
        #     10)
        # self.sct_subscription  # prevent unused variable warning

        self.request_counter = 0
        self.num_acks = 0

        self.declare_parameter('angle', 91.0)

        self.cli = self.create_client(SetPositions, 'set_positions')
        self.event_cli = self.create_client(SetEvent, 'set_event')
        self.sta_cli = self.create_client(AskSta, 'ask_sta')
        #self.cli = self.create_client(SetPositions, 'safety_service')

        while not self.cli.wait_for_service(timeout_sec=1.0):
            if(rclpy.ok()):
                self.get_logger().info('service not available, waiting again...')
                return

        self.req = SetPositions.Request()
        self.ask = AskSta.Request()
        
        self.cur_pos = np.array([])
        self.cur_torques = np.array([])
        self.previous_torques = np.array([])
        self.k = np.array([0.1, 0.1, 0.1, 0.1, 1, 0.1]) #joint
        self.torque_diff_threshold = 1.0
        
        self.stored_torques = np.empty((0, 6))
        self.windows_size = 20
        self.average_torques = np.array([])
        
        self.goal_position = np.array([])
        self.previous_goal_position_reached = False
        self.last_request = np.array([])

        self.cur_pos_cartesian = np.array([])
        self.tool_pose = np.array([])

        self.position_delta_max = 0.020 #meters 
        self.temp = 0

        self.queue_tag_event = SetEvent.Request()
        self.sta_response_val = False

        self.current_tag = 0

    def feedback_callback(self, msg):
        self.cur_pos_cartesian = np.asarray(msg.tool_pose)
        self.tcp_force = np.asarray(msg.tcp_force)
        # print("TCP Force: ", msg.tcp_force)
        print("Tool Position: ", self.cur_pos_cartesian)
        print("Tool Pose: ", self.tool_pose)
        print("TCP Force X: ", self.tcp_force[0])
        self.stiff_arm_control()
        # self.send_requests_tool()
        #self.cur_pos = np.asarray([math.degrees(angle) for angle in msg.joint_pos])
        # self.cur_torques = np.array(msg.joint_tor)
        # if(self.previous_torques.size == 0): #if previous_torques is empty
        #     print("setting previous torques to current")
        #     self.previous_torques = self.cur_torques
        # print("TCP Force: ", msg.tcp_force)
        # self.moving_average()
        # self.send_requests_joint()
        # self.previous_torques = self.cur_torques
    
    # def sct_callback(self, msg):
    #     if msg.script == 'OK':
    #         self.num_acks += 1

    def stiff_arm_control(self):
        force_max = 60.0 #newtons
        force_min = -60.0 #newtons
        vel_max = 80.0 # mm/s
        vel_min = -80.0 # mm/s

        gain = 3.0

        # keep velocity of the base within a range
        if self.tcp_force[0] > force_max:
            self.tcp_force[0] = force_max
        elif self.tcp_force[0] < force_min:
            self.tcp_force[0] = force_min

        #if force is < 10N in either direction
        if abs(self.tcp_force[0] - 0) < 1.0: 
            self.tcp_force[0] = 0.0

        #control law
        self.current_twist.linear.x = gain * self.tcp_force[0]
        
        # keep velocity of the base within a range
        if self.current_twist.linear.x > vel_max:
            self.current_twist.linear.x = vel_max
        elif self.current_twist.linear.x < vel_min:
            self.current_twist.linear.x = vel_min

        # publish the velocity
        self.twist_publisher.publish(self.current_twist)

    def sta_callback(self, msg):
        """
        Called if ask_sta (sta_request) is made.
        If ask is made, check if the current queue tag is true, indicates previous motion is complete, then set sta_response_val true
        If current queue tag is false, then set sta_response_val false
        """
        # print('-------STA_CALLBACK---------')
        # print("subcmd: ", msg.subcmd)
        # print("subdata: ", msg.subdata)
        if('true' and str(self.current_tag) in msg.subdata):
            self.sta_response_val = True
        else:
            self.sta_response_val = False
        # print('-------STA_CALLBACK_END---------')
    
    def config_queue_tag(self, tag_int):
        self.queue_tag_event.func = SetEvent.Request.WAIT_TAG
        self.queue_tag_event.arg0 = tag_int #tag number
        self.queue_tag_event.arg1 = -1 #timeout in ms.

    def config_and_call_sta_ask(self, tag_number):
        # print('STA ASK')
        self.ask.subcmd = "01"
        self.ask.subdata = str(tag_number)
        self.ask.wait_time = 4.0
        print(self.ask)
        self.future = self.sta_cli.call_async(self.ask)

    def send_requests_tool(self):
        print("current_tag: ", self.current_tag)

        if self.current_tag != 0:
            self.config_and_call_sta_ask(self.current_tag)

        self.req.motion_type = SetPositions.Request.PTP_T

        # print("Tool Position: ", self.cur_pos_cartesian)
        # print("Tool Pose: ", self.tool_pose)
        # print("TCP Force X: ", self.tcp_force[0])

        # print("control law output: ", self.control_law_tool(0))

        # POSE IS IN RADIANS (RX, RY, RZ)
        # desired_tool_position_mm = [self.control_law_tool(0), self.cur_pos_cartesian[1], self.cur_pos_cartesian[2], 3.14, 0.0, 0.0] 
        desired_tool_position_mm = [710/1000, self.cur_pos_cartesian[1], self.cur_pos_cartesian[2], 3.14, 0.0, 0.0] 
        desired_tool_position_mm2 = [355/1000, self.cur_pos_cartesian[1], self.cur_pos_cartesian[2], 3.14, 0.0, 0.0] 
        self.req.positions = desired_tool_position_mm

        # print("self.req.positions: ", self.req.positions)
        # self.req.positions = [0.174533, -0.005934119, 2.46283411, -0.00872665, 1.1229448, 0.26284659]
        
        self.req.velocity = 5.0
        self.req.acc_time = 0.2
        self.req.blend_percentage = 10
        self.req.fine_goal = False

        if self.temp == 0:
            print("making singular request")
            self.config_queue_tag(1)
            self.current_tag += 1
            self.future = self.cli.call_async(self.req)
            self.future = self.event_cli.call_async(self.queue_tag_event)
            self.goal_position = np.asarray(desired_tool_position_mm)
            self.temp = 1
        if self.temp == 1:
            if self.sta_response_val:
            # if all(np.abs(self.cur_pos_cartesian - self.goal_position) <= 0.1): 
                print("making 2nd singular request")
                time.sleep(3)
                self.config_queue_tag(2)
                self.current_tag += 1
                self.req.positions = desired_tool_position_mm2
                self.future = self.cli.call_async(self.req)
                self.future = self.event_cli.call_async(self.queue_tag_event)
                self.temp = 2 

        # if(val is same):
        #     dont do anything
        # else:
        #     update counter
        #     send request
        # if the goal position array is empty (first time through), then set it to the req positions
        # this check could be moved out to the feedback callback?
        # if self.goal_position.size == 0: 
        #     self.goal_position = np.asarray(desired_tool_position_mm) # assignment to convert python array to np array
        #     self.future = self.cli.call_async(self.req)
        #     print("MAKING INITIAL MOVE REQUEST")
        #     return
        # else: # if there is something in the array, then go ahead and check if the reported(feedback) position is at the goal position.
        #     # check to make sure the arrays are sized properly for the abs value math done after
        #     if self.cur_pos_cartesian.shape != self.goal_position.shape:
        #         raise ValueError("Both arrays must have the same shape")

        #     # checks abs value between corresponding elements in each array meet are close enough to the goal.
        #     # only true if all joints have reached the goal positions. Checked by using all()
        #     print("abs: ", np.abs(self.cur_pos_cartesian - self.goal_position))
        #     if all(np.abs(self.cur_pos_cartesian - self.goal_position) <= 0.1):
        #         self.previous_goal_position_reached = True
        #         print("PREVIOUS REQUEST REACHED")
        #     else:
        #         self.previous_goal_position_reached = False
        #         print("PREVIOUS REQUEST NOT REACHED")

        # if self.previous_goal_position_reached:
        #     if all(np.abs(self.cur_pos_cartesian - np.asarray(desired_tool_position_mm)) <= 0.01):
        #         print("REQUEST NOT DIFFERENT")
        #         return
        #     else:
        #         self.future = self.cli.call_async(self.req)
        #         print("MAKING NEW MOVE REQUEST")
        return
    
    def control_law_tool(self, axis):
        # gain = 0.0025
        tcp_threshold = 10.0 #Newtons
        gain = 0.0025
        if abs(self.tcp_force[axis]) < tcp_threshold : 
            self.tcp_force[axis] = 0.0
            print("setting tcp force to 0")
        
        new_position = self.cur_pos_cartesian[axis] + (gain * self.tcp_force[axis])

        # if new position generated by control law is over threshold, then return the current position + or - the max
        if new_position < self.cur_pos_cartesian[axis] - self.position_delta_max:
            print("goal is under minimum: ", self.cur_pos_cartesian[axis] - self.position_delta_max)
            return self.cur_pos_cartesian[axis] - self.position_delta_max
        elif new_position > self.cur_pos_cartesian[axis] + self.position_delta_max:
            print("goal is over maximum: ", self.cur_pos_cartesian[axis] + self.position_delta_max)
            return self.cur_pos_cartesian[axis] + self.position_delta_max
        else:
            print("goal is within range: ", new_position)
            return new_position

    def send_requests_joint(self):
        """
        Fills out the set positions request to be made to TM_Driver.
        desired_joint _positions_degrees is filled out with the control law output for each joint
        self.req.positions holds the radians equivalent of desired_joint _positions_degrees
        
        perform check to send new request based on previous position request being reached.
            - initial case: set goal_position to the request just generated, make the request, then return right away
            - not initial case: check if current_positions of all joints have reached goal_position (check if abs value is within range)
                if within range, then set previous_goal_position_reached to true
        
        if previous_goal_position_reached is true
            set new goal to be the request just generated so that when you check the next time they are synced.
            make request
        return
        """

        self.req.motion_type = SetPositions.Request.PTP_J
        my_param = self.get_parameter('angle').get_parameter_value().double_value

        print("self.cur_pos: ", self.cur_pos)
        # print("self.goal_position: ", self.goal_position)
        # print(f"self.cur_torques {self.cur_torques[4]}")
        # print(f"self.cur_torques {type(self.cur_torques)}")

        desired_joint_positions_degrees = [10, 0, 90, 0, self.control_law_joint(4), 10] #valid
        #desired_joint_positions_degrees = [10, 0, 90, 0, 60, 10] #valid
        #desired_joint_positions_degrees = [-11, 5, 130, 20, 60, 10] #invalid
        # print("desired_joint_positions_degrees: ", desired_joint_positions_degrees)
        self.req.positions = [math.radians(angle) for angle in desired_joint_positions_degrees]

        #print("self.req.positions: ", self.req.positions)
        # self.req.positions = [0.174533, -0.005934119, 2.46283411, -0.00872665, 1.1229448, 0.26284659]
        
        self.req.velocity = 1.0
        self.req.acc_time = 0.2
        self.req.blend_percentage = 10
        self.req.fine_goal = False

        # if the goal position array is empty (first time through), then set it to the req positions
        # this check could be moved out to the feedback callback?
        if self.goal_position.size == 0: 
            self.goal_position = np.asarray(desired_joint_positions_degrees) # assignment to convert python array to np array
            self.future = self.cli.call_async(self.req)
            print("MAKING INITIAL MOVE REQUEST")
            return
        else: # if there is something in the array, then go ahead and check if the reported(feedback) position is at the goal position.
            # check to make sure the arrays are sized properly for the abs value math done after
            if self.cur_pos.shape != self.goal_position.shape:
                raise ValueError("Both arrays must have the same shape")

            # checks abs value between corresponding elements in each array meet are close enough to the goal.
            # only true if all joints have reached the goal positions. Checked by using all()
            print("abs: ", np.abs(self.cur_pos - self.goal_position))
            if all(np.abs(self.cur_pos - self.goal_position) <= 0.05):
                self.previous_goal_position_reached = True
                print("PREVIOUS REQUEST REACHED")
            else:
                self.previous_goal_position_reached = False
            

        if self.previous_goal_position_reached:
            # check if the desired position is the current position, only make request if they are different
            if all(np.abs(self.cur_pos - np.asarray(desired_joint_positions_degrees)) <= 0.05):
                print("REQUEST NOT DIFFERENT")
                return
            else:
                self.goal_position = np.asarray(desired_joint_positions_degrees)
                self.future = self.cli.call_async(self.req)
                print("MAKING NEW MOVE REQUEST")
        return
            
    def control_law_joint(self, joint):
        torque_dif = self.average_torques[0 ,joint] - self.previous_torques[joint]
        position_des = self.cur_pos[joint] + self.k[joint] * (torque_dif)
        # print("position des: ", position_des)
        print("torque dif: ", torque_dif)
        # print("torque dif threshold: ", self.torque_diff_threshold)
        return position_des if abs(torque_dif) > self.torque_diff_threshold else self.cur_pos[joint]

    def moving_average(self):
        self.manage_2d_array(new_row=self.cur_torques, max_rows=self.windows_size)
        
        self.average_torques = self.average_columns()
        
        #print("pre flatten: ", self.average_torques)
        
        self.average_torques = self.average_torques.reshape(1,6)
        
        #print("post flatten: ", self.average_torques)
        #print("average torques shape: ", self.average_torques.shape)
        
        #print("index 5: ", self.average_torques[0, 4])
        
        # print(self.previous_torques.shape)
        # print("previous torque: ", self.previous_torques[4])
    
    def manage_2d_array(self, new_row, max_rows):
        """
        Appends a new row to the 2D array and removes the oldest row if the 2D array exceeds max_rows.

        Parameters:
        main_array (np.ndarray): The 2D array to which the new row will be added.
        new_row (list or np.ndarray): The new row to add to the 2D array.
        max_rows (int): The maximum number of rows the 2D array can have.

        Returns:
        np.ndarray: The updated 2D array.
        """
        if not isinstance(new_row, np.ndarray):
            new_row = np.array(new_row)
        
        self.stored_torques = np.vstack([self.stored_torques, new_row])
        if self.stored_torques.shape[0] > max_rows:
            self.stored_torques = self.stored_torques[1:]
        
        return self.stored_torques
    
    def average_columns(self):
        """
        Calculates the average of each column in a 2D NumPy array.

        Parameters:
        main_array (np.ndarray): The 2D array for which column averages will be calculated.

        Returns:
        np.ndarray: An array containing the averages of each column.
        """
        if self.stored_torques.size == 0:
            return np.array([])
        column_averages = np.mean(self.stored_torques, axis=0)
        return column_averages


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
import rclpy
from rclpy.node import Node

from tm_msgs.srv import SetPositions
class ArmService(Node):

    def __init__(self):
        super().__init__('arm_service')

        self.cli = self.create_client(SetPositions, 'set_positions')

        while not self.cli.wait_for_service(timeout_sec=1.0):
            if(rclpy.ok()):
                self.get_logger().info('service not available, waiting again...')
                return

        self.req = SetPositions.Request()

    def send_requests(self):

        self.req.motion_type = SetPositions.Request.PTP_J

        self.req.positions = [0.174533, -0.005934119, 2.46283411,
                                -0.00872665, 1.1229448, 0.26284659]
        
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
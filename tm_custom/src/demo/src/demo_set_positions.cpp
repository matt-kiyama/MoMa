#include "rclcpp/rclcpp.hpp"
#include "tm_msgs/srv/set_positions.hpp"

#include <chrono>
#include <cstdlib>
#include <memory>

using namespace std::chrono_literals;

int main(int argc, char **argv)
{
  rclcpp::init(argc, argv);


  std::shared_ptr<rclcpp::Node> node = rclcpp::Node::make_shared("demo_set_positions");
  rclcpp::Client<tm_msgs::srv::SetPositions>::SharedPtr client =
    node->create_client<tm_msgs::srv::SetPositions>("set_positions");
  
  auto request = std::make_shared<tm_msgs::srv::SetPositions::Request>();
  request->motion_type = tm_msgs::srv::SetPositions::Request::PTP_J;
  request->positions.push_back(0.174533); //joint 1
  request->positions.push_back(-0.005934119); //joint 2
  request->positions.push_back(2.46283411); //joint 3
  request->positions.push_back(-0.00872665); //joint 4
  request->positions.push_back(1.1229448); //joint 5
  request->positions.push_back(0.26284659); //joint 6
  request->velocity = 2.0;//rad/s
  request->acc_time = 0.2;
  request->blend_percentage = 10;
  request->fine_goal  = false;
  for (double &x : request->positions)
    std::cout << x << " ";

  while (!client->wait_for_service(1s)) {
    if (!rclcpp::ok()) {
      RCLCPP_ERROR_STREAM(rclcpp::get_logger("rclcpp"), "Interrupted while waiting for the service. Exiting.");
      return false;
    }
    RCLCPP_INFO_STREAM(rclcpp::get_logger("rclcpp"), "service not available, waiting again...");
  }

  auto result = client->async_send_request(request);
  // Wait for the result.
  if (rclcpp::spin_until_future_complete(node, result) ==
    rclcpp::FutureReturnCode::SUCCESS)
    //rclcpp::executor::FutureReturnCode::SUCCESS)
  {
    if(result.get()->ok){
      RCLCPP_INFO_STREAM(rclcpp::get_logger("rclcpp"),"OK");
    } else{
      RCLCPP_INFO_STREAM(rclcpp::get_logger("rclcpp"),"not OK");
    }

  } else {
    RCLCPP_ERROR_STREAM(rclcpp::get_logger("rclcpp"), "Failed to call service");
  }
  return true;

  rclcpp::shutdown();
  return 0;
}

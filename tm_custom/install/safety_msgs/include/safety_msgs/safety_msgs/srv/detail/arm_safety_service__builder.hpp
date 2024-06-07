// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from safety_msgs:srv/ArmSafetyService.idl
// generated code does not contain a copyright notice

#ifndef SAFETY_MSGS__SRV__DETAIL__ARM_SAFETY_SERVICE__BUILDER_HPP_
#define SAFETY_MSGS__SRV__DETAIL__ARM_SAFETY_SERVICE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "safety_msgs/srv/detail/arm_safety_service__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace safety_msgs
{

namespace srv
{

namespace builder
{

class Init_ArmSafetyService_Request_fine_goal
{
public:
  explicit Init_ArmSafetyService_Request_fine_goal(::safety_msgs::srv::ArmSafetyService_Request & msg)
  : msg_(msg)
  {}
  ::safety_msgs::srv::ArmSafetyService_Request fine_goal(::safety_msgs::srv::ArmSafetyService_Request::_fine_goal_type arg)
  {
    msg_.fine_goal = std::move(arg);
    return std::move(msg_);
  }

private:
  ::safety_msgs::srv::ArmSafetyService_Request msg_;
};

class Init_ArmSafetyService_Request_blend_percentage
{
public:
  explicit Init_ArmSafetyService_Request_blend_percentage(::safety_msgs::srv::ArmSafetyService_Request & msg)
  : msg_(msg)
  {}
  Init_ArmSafetyService_Request_fine_goal blend_percentage(::safety_msgs::srv::ArmSafetyService_Request::_blend_percentage_type arg)
  {
    msg_.blend_percentage = std::move(arg);
    return Init_ArmSafetyService_Request_fine_goal(msg_);
  }

private:
  ::safety_msgs::srv::ArmSafetyService_Request msg_;
};

class Init_ArmSafetyService_Request_acc_time
{
public:
  explicit Init_ArmSafetyService_Request_acc_time(::safety_msgs::srv::ArmSafetyService_Request & msg)
  : msg_(msg)
  {}
  Init_ArmSafetyService_Request_blend_percentage acc_time(::safety_msgs::srv::ArmSafetyService_Request::_acc_time_type arg)
  {
    msg_.acc_time = std::move(arg);
    return Init_ArmSafetyService_Request_blend_percentage(msg_);
  }

private:
  ::safety_msgs::srv::ArmSafetyService_Request msg_;
};

class Init_ArmSafetyService_Request_velocity
{
public:
  explicit Init_ArmSafetyService_Request_velocity(::safety_msgs::srv::ArmSafetyService_Request & msg)
  : msg_(msg)
  {}
  Init_ArmSafetyService_Request_acc_time velocity(::safety_msgs::srv::ArmSafetyService_Request::_velocity_type arg)
  {
    msg_.velocity = std::move(arg);
    return Init_ArmSafetyService_Request_acc_time(msg_);
  }

private:
  ::safety_msgs::srv::ArmSafetyService_Request msg_;
};

class Init_ArmSafetyService_Request_positions
{
public:
  explicit Init_ArmSafetyService_Request_positions(::safety_msgs::srv::ArmSafetyService_Request & msg)
  : msg_(msg)
  {}
  Init_ArmSafetyService_Request_velocity positions(::safety_msgs::srv::ArmSafetyService_Request::_positions_type arg)
  {
    msg_.positions = std::move(arg);
    return Init_ArmSafetyService_Request_velocity(msg_);
  }

private:
  ::safety_msgs::srv::ArmSafetyService_Request msg_;
};

class Init_ArmSafetyService_Request_motion_type
{
public:
  Init_ArmSafetyService_Request_motion_type()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ArmSafetyService_Request_positions motion_type(::safety_msgs::srv::ArmSafetyService_Request::_motion_type_type arg)
  {
    msg_.motion_type = std::move(arg);
    return Init_ArmSafetyService_Request_positions(msg_);
  }

private:
  ::safety_msgs::srv::ArmSafetyService_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::safety_msgs::srv::ArmSafetyService_Request>()
{
  return safety_msgs::srv::builder::Init_ArmSafetyService_Request_motion_type();
}

}  // namespace safety_msgs


namespace safety_msgs
{

namespace srv
{

namespace builder
{

class Init_ArmSafetyService_Response_ok
{
public:
  Init_ArmSafetyService_Response_ok()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::safety_msgs::srv::ArmSafetyService_Response ok(::safety_msgs::srv::ArmSafetyService_Response::_ok_type arg)
  {
    msg_.ok = std::move(arg);
    return std::move(msg_);
  }

private:
  ::safety_msgs::srv::ArmSafetyService_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::safety_msgs::srv::ArmSafetyService_Response>()
{
  return safety_msgs::srv::builder::Init_ArmSafetyService_Response_ok();
}

}  // namespace safety_msgs

#endif  // SAFETY_MSGS__SRV__DETAIL__ARM_SAFETY_SERVICE__BUILDER_HPP_

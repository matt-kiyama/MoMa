// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from techman_robot_msgs:srv/TechmanRobotCommand.idl
// generated code does not contain a copyright notice

#ifndef TECHMAN_ROBOT_MSGS__SRV__DETAIL__TECHMAN_ROBOT_COMMAND__TRAITS_HPP_
#define TECHMAN_ROBOT_MSGS__SRV__DETAIL__TECHMAN_ROBOT_COMMAND__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "techman_robot_msgs/srv/detail/techman_robot_command__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace techman_robot_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const TechmanRobotCommand_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: command
  {
    out << "command: ";
    rosidl_generator_traits::value_to_yaml(msg.command, out);
    out << ", ";
  }

  // member: command_parameter_string
  {
    out << "command_parameter_string: ";
    rosidl_generator_traits::value_to_yaml(msg.command_parameter_string, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const TechmanRobotCommand_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: command
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "command: ";
    rosidl_generator_traits::value_to_yaml(msg.command, out);
    out << "\n";
  }

  // member: command_parameter_string
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "command_parameter_string: ";
    rosidl_generator_traits::value_to_yaml(msg.command_parameter_string, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const TechmanRobotCommand_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace techman_robot_msgs

namespace rosidl_generator_traits
{

[[deprecated("use techman_robot_msgs::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const techman_robot_msgs::srv::TechmanRobotCommand_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  techman_robot_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use techman_robot_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const techman_robot_msgs::srv::TechmanRobotCommand_Request & msg)
{
  return techman_robot_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<techman_robot_msgs::srv::TechmanRobotCommand_Request>()
{
  return "techman_robot_msgs::srv::TechmanRobotCommand_Request";
}

template<>
inline const char * name<techman_robot_msgs::srv::TechmanRobotCommand_Request>()
{
  return "techman_robot_msgs/srv/TechmanRobotCommand_Request";
}

template<>
struct has_fixed_size<techman_robot_msgs::srv::TechmanRobotCommand_Request>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<techman_robot_msgs::srv::TechmanRobotCommand_Request>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<techman_robot_msgs::srv::TechmanRobotCommand_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace techman_robot_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const TechmanRobotCommand_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: is_success
  {
    out << "is_success: ";
    rosidl_generator_traits::value_to_yaml(msg.is_success, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const TechmanRobotCommand_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: is_success
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "is_success: ";
    rosidl_generator_traits::value_to_yaml(msg.is_success, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const TechmanRobotCommand_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace techman_robot_msgs

namespace rosidl_generator_traits
{

[[deprecated("use techman_robot_msgs::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const techman_robot_msgs::srv::TechmanRobotCommand_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  techman_robot_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use techman_robot_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const techman_robot_msgs::srv::TechmanRobotCommand_Response & msg)
{
  return techman_robot_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<techman_robot_msgs::srv::TechmanRobotCommand_Response>()
{
  return "techman_robot_msgs::srv::TechmanRobotCommand_Response";
}

template<>
inline const char * name<techman_robot_msgs::srv::TechmanRobotCommand_Response>()
{
  return "techman_robot_msgs/srv/TechmanRobotCommand_Response";
}

template<>
struct has_fixed_size<techman_robot_msgs::srv::TechmanRobotCommand_Response>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<techman_robot_msgs::srv::TechmanRobotCommand_Response>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<techman_robot_msgs::srv::TechmanRobotCommand_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<techman_robot_msgs::srv::TechmanRobotCommand>()
{
  return "techman_robot_msgs::srv::TechmanRobotCommand";
}

template<>
inline const char * name<techman_robot_msgs::srv::TechmanRobotCommand>()
{
  return "techman_robot_msgs/srv/TechmanRobotCommand";
}

template<>
struct has_fixed_size<techman_robot_msgs::srv::TechmanRobotCommand>
  : std::integral_constant<
    bool,
    has_fixed_size<techman_robot_msgs::srv::TechmanRobotCommand_Request>::value &&
    has_fixed_size<techman_robot_msgs::srv::TechmanRobotCommand_Response>::value
  >
{
};

template<>
struct has_bounded_size<techman_robot_msgs::srv::TechmanRobotCommand>
  : std::integral_constant<
    bool,
    has_bounded_size<techman_robot_msgs::srv::TechmanRobotCommand_Request>::value &&
    has_bounded_size<techman_robot_msgs::srv::TechmanRobotCommand_Response>::value
  >
{
};

template<>
struct is_service<techman_robot_msgs::srv::TechmanRobotCommand>
  : std::true_type
{
};

template<>
struct is_service_request<techman_robot_msgs::srv::TechmanRobotCommand_Request>
  : std::true_type
{
};

template<>
struct is_service_response<techman_robot_msgs::srv::TechmanRobotCommand_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // TECHMAN_ROBOT_MSGS__SRV__DETAIL__TECHMAN_ROBOT_COMMAND__TRAITS_HPP_

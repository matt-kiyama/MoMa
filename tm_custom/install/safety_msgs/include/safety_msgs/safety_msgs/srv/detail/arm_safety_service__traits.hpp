// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from safety_msgs:srv/ArmSafetyService.idl
// generated code does not contain a copyright notice

#ifndef SAFETY_MSGS__SRV__DETAIL__ARM_SAFETY_SERVICE__TRAITS_HPP_
#define SAFETY_MSGS__SRV__DETAIL__ARM_SAFETY_SERVICE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "safety_msgs/srv/detail/arm_safety_service__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace safety_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const ArmSafetyService_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: motion_type
  {
    out << "motion_type: ";
    rosidl_generator_traits::value_to_yaml(msg.motion_type, out);
    out << ", ";
  }

  // member: positions
  {
    if (msg.positions.size() == 0) {
      out << "positions: []";
    } else {
      out << "positions: [";
      size_t pending_items = msg.positions.size();
      for (auto item : msg.positions) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: velocity
  {
    out << "velocity: ";
    rosidl_generator_traits::value_to_yaml(msg.velocity, out);
    out << ", ";
  }

  // member: acc_time
  {
    out << "acc_time: ";
    rosidl_generator_traits::value_to_yaml(msg.acc_time, out);
    out << ", ";
  }

  // member: blend_percentage
  {
    out << "blend_percentage: ";
    rosidl_generator_traits::value_to_yaml(msg.blend_percentage, out);
    out << ", ";
  }

  // member: fine_goal
  {
    out << "fine_goal: ";
    rosidl_generator_traits::value_to_yaml(msg.fine_goal, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ArmSafetyService_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: motion_type
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "motion_type: ";
    rosidl_generator_traits::value_to_yaml(msg.motion_type, out);
    out << "\n";
  }

  // member: positions
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.positions.size() == 0) {
      out << "positions: []\n";
    } else {
      out << "positions:\n";
      for (auto item : msg.positions) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: velocity
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "velocity: ";
    rosidl_generator_traits::value_to_yaml(msg.velocity, out);
    out << "\n";
  }

  // member: acc_time
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "acc_time: ";
    rosidl_generator_traits::value_to_yaml(msg.acc_time, out);
    out << "\n";
  }

  // member: blend_percentage
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "blend_percentage: ";
    rosidl_generator_traits::value_to_yaml(msg.blend_percentage, out);
    out << "\n";
  }

  // member: fine_goal
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fine_goal: ";
    rosidl_generator_traits::value_to_yaml(msg.fine_goal, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ArmSafetyService_Request & msg, bool use_flow_style = false)
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

}  // namespace safety_msgs

namespace rosidl_generator_traits
{

[[deprecated("use safety_msgs::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const safety_msgs::srv::ArmSafetyService_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  safety_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use safety_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const safety_msgs::srv::ArmSafetyService_Request & msg)
{
  return safety_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<safety_msgs::srv::ArmSafetyService_Request>()
{
  return "safety_msgs::srv::ArmSafetyService_Request";
}

template<>
inline const char * name<safety_msgs::srv::ArmSafetyService_Request>()
{
  return "safety_msgs/srv/ArmSafetyService_Request";
}

template<>
struct has_fixed_size<safety_msgs::srv::ArmSafetyService_Request>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<safety_msgs::srv::ArmSafetyService_Request>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<safety_msgs::srv::ArmSafetyService_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace safety_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const ArmSafetyService_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: ok
  {
    out << "ok: ";
    rosidl_generator_traits::value_to_yaml(msg.ok, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ArmSafetyService_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: ok
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "ok: ";
    rosidl_generator_traits::value_to_yaml(msg.ok, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ArmSafetyService_Response & msg, bool use_flow_style = false)
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

}  // namespace safety_msgs

namespace rosidl_generator_traits
{

[[deprecated("use safety_msgs::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const safety_msgs::srv::ArmSafetyService_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  safety_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use safety_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const safety_msgs::srv::ArmSafetyService_Response & msg)
{
  return safety_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<safety_msgs::srv::ArmSafetyService_Response>()
{
  return "safety_msgs::srv::ArmSafetyService_Response";
}

template<>
inline const char * name<safety_msgs::srv::ArmSafetyService_Response>()
{
  return "safety_msgs/srv/ArmSafetyService_Response";
}

template<>
struct has_fixed_size<safety_msgs::srv::ArmSafetyService_Response>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<safety_msgs::srv::ArmSafetyService_Response>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<safety_msgs::srv::ArmSafetyService_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<safety_msgs::srv::ArmSafetyService>()
{
  return "safety_msgs::srv::ArmSafetyService";
}

template<>
inline const char * name<safety_msgs::srv::ArmSafetyService>()
{
  return "safety_msgs/srv/ArmSafetyService";
}

template<>
struct has_fixed_size<safety_msgs::srv::ArmSafetyService>
  : std::integral_constant<
    bool,
    has_fixed_size<safety_msgs::srv::ArmSafetyService_Request>::value &&
    has_fixed_size<safety_msgs::srv::ArmSafetyService_Response>::value
  >
{
};

template<>
struct has_bounded_size<safety_msgs::srv::ArmSafetyService>
  : std::integral_constant<
    bool,
    has_bounded_size<safety_msgs::srv::ArmSafetyService_Request>::value &&
    has_bounded_size<safety_msgs::srv::ArmSafetyService_Response>::value
  >
{
};

template<>
struct is_service<safety_msgs::srv::ArmSafetyService>
  : std::true_type
{
};

template<>
struct is_service_request<safety_msgs::srv::ArmSafetyService_Request>
  : std::true_type
{
};

template<>
struct is_service_response<safety_msgs::srv::ArmSafetyService_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // SAFETY_MSGS__SRV__DETAIL__ARM_SAFETY_SERVICE__TRAITS_HPP_

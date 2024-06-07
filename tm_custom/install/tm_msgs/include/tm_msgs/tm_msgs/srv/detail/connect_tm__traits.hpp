// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from tm_msgs:srv/ConnectTM.idl
// generated code does not contain a copyright notice

#ifndef TM_MSGS__SRV__DETAIL__CONNECT_TM__TRAITS_HPP_
#define TM_MSGS__SRV__DETAIL__CONNECT_TM__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "tm_msgs/srv/detail/connect_tm__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace tm_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const ConnectTM_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: server
  {
    out << "server: ";
    rosidl_generator_traits::value_to_yaml(msg.server, out);
    out << ", ";
  }

  // member: connect
  {
    out << "connect: ";
    rosidl_generator_traits::value_to_yaml(msg.connect, out);
    out << ", ";
  }

  // member: reconnect
  {
    out << "reconnect: ";
    rosidl_generator_traits::value_to_yaml(msg.reconnect, out);
    out << ", ";
  }

  // member: timeout
  {
    out << "timeout: ";
    rosidl_generator_traits::value_to_yaml(msg.timeout, out);
    out << ", ";
  }

  // member: timeval
  {
    out << "timeval: ";
    rosidl_generator_traits::value_to_yaml(msg.timeval, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ConnectTM_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: server
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "server: ";
    rosidl_generator_traits::value_to_yaml(msg.server, out);
    out << "\n";
  }

  // member: connect
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "connect: ";
    rosidl_generator_traits::value_to_yaml(msg.connect, out);
    out << "\n";
  }

  // member: reconnect
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "reconnect: ";
    rosidl_generator_traits::value_to_yaml(msg.reconnect, out);
    out << "\n";
  }

  // member: timeout
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "timeout: ";
    rosidl_generator_traits::value_to_yaml(msg.timeout, out);
    out << "\n";
  }

  // member: timeval
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "timeval: ";
    rosidl_generator_traits::value_to_yaml(msg.timeval, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ConnectTM_Request & msg, bool use_flow_style = false)
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

}  // namespace tm_msgs

namespace rosidl_generator_traits
{

[[deprecated("use tm_msgs::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const tm_msgs::srv::ConnectTM_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  tm_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use tm_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const tm_msgs::srv::ConnectTM_Request & msg)
{
  return tm_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<tm_msgs::srv::ConnectTM_Request>()
{
  return "tm_msgs::srv::ConnectTM_Request";
}

template<>
inline const char * name<tm_msgs::srv::ConnectTM_Request>()
{
  return "tm_msgs/srv/ConnectTM_Request";
}

template<>
struct has_fixed_size<tm_msgs::srv::ConnectTM_Request>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<tm_msgs::srv::ConnectTM_Request>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<tm_msgs::srv::ConnectTM_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace tm_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const ConnectTM_Response & msg,
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
  const ConnectTM_Response & msg,
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

inline std::string to_yaml(const ConnectTM_Response & msg, bool use_flow_style = false)
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

}  // namespace tm_msgs

namespace rosidl_generator_traits
{

[[deprecated("use tm_msgs::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const tm_msgs::srv::ConnectTM_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  tm_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use tm_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const tm_msgs::srv::ConnectTM_Response & msg)
{
  return tm_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<tm_msgs::srv::ConnectTM_Response>()
{
  return "tm_msgs::srv::ConnectTM_Response";
}

template<>
inline const char * name<tm_msgs::srv::ConnectTM_Response>()
{
  return "tm_msgs/srv/ConnectTM_Response";
}

template<>
struct has_fixed_size<tm_msgs::srv::ConnectTM_Response>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<tm_msgs::srv::ConnectTM_Response>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<tm_msgs::srv::ConnectTM_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<tm_msgs::srv::ConnectTM>()
{
  return "tm_msgs::srv::ConnectTM";
}

template<>
inline const char * name<tm_msgs::srv::ConnectTM>()
{
  return "tm_msgs/srv/ConnectTM";
}

template<>
struct has_fixed_size<tm_msgs::srv::ConnectTM>
  : std::integral_constant<
    bool,
    has_fixed_size<tm_msgs::srv::ConnectTM_Request>::value &&
    has_fixed_size<tm_msgs::srv::ConnectTM_Response>::value
  >
{
};

template<>
struct has_bounded_size<tm_msgs::srv::ConnectTM>
  : std::integral_constant<
    bool,
    has_bounded_size<tm_msgs::srv::ConnectTM_Request>::value &&
    has_bounded_size<tm_msgs::srv::ConnectTM_Response>::value
  >
{
};

template<>
struct is_service<tm_msgs::srv::ConnectTM>
  : std::true_type
{
};

template<>
struct is_service_request<tm_msgs::srv::ConnectTM_Request>
  : std::true_type
{
};

template<>
struct is_service_response<tm_msgs::srv::ConnectTM_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // TM_MSGS__SRV__DETAIL__CONNECT_TM__TRAITS_HPP_

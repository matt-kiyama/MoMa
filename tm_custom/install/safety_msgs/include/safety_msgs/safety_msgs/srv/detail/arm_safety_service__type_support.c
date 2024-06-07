// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from safety_msgs:srv/ArmSafetyService.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "safety_msgs/srv/detail/arm_safety_service__rosidl_typesupport_introspection_c.h"
#include "safety_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "safety_msgs/srv/detail/arm_safety_service__functions.h"
#include "safety_msgs/srv/detail/arm_safety_service__struct.h"


// Include directives for member types
// Member `positions`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void safety_msgs__srv__ArmSafetyService_Request__rosidl_typesupport_introspection_c__ArmSafetyService_Request_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  safety_msgs__srv__ArmSafetyService_Request__init(message_memory);
}

void safety_msgs__srv__ArmSafetyService_Request__rosidl_typesupport_introspection_c__ArmSafetyService_Request_fini_function(void * message_memory)
{
  safety_msgs__srv__ArmSafetyService_Request__fini(message_memory);
}

size_t safety_msgs__srv__ArmSafetyService_Request__rosidl_typesupport_introspection_c__size_function__ArmSafetyService_Request__positions(
  const void * untyped_member)
{
  const rosidl_runtime_c__double__Sequence * member =
    (const rosidl_runtime_c__double__Sequence *)(untyped_member);
  return member->size;
}

const void * safety_msgs__srv__ArmSafetyService_Request__rosidl_typesupport_introspection_c__get_const_function__ArmSafetyService_Request__positions(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__double__Sequence * member =
    (const rosidl_runtime_c__double__Sequence *)(untyped_member);
  return &member->data[index];
}

void * safety_msgs__srv__ArmSafetyService_Request__rosidl_typesupport_introspection_c__get_function__ArmSafetyService_Request__positions(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__double__Sequence * member =
    (rosidl_runtime_c__double__Sequence *)(untyped_member);
  return &member->data[index];
}

void safety_msgs__srv__ArmSafetyService_Request__rosidl_typesupport_introspection_c__fetch_function__ArmSafetyService_Request__positions(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const double * item =
    ((const double *)
    safety_msgs__srv__ArmSafetyService_Request__rosidl_typesupport_introspection_c__get_const_function__ArmSafetyService_Request__positions(untyped_member, index));
  double * value =
    (double *)(untyped_value);
  *value = *item;
}

void safety_msgs__srv__ArmSafetyService_Request__rosidl_typesupport_introspection_c__assign_function__ArmSafetyService_Request__positions(
  void * untyped_member, size_t index, const void * untyped_value)
{
  double * item =
    ((double *)
    safety_msgs__srv__ArmSafetyService_Request__rosidl_typesupport_introspection_c__get_function__ArmSafetyService_Request__positions(untyped_member, index));
  const double * value =
    (const double *)(untyped_value);
  *item = *value;
}

bool safety_msgs__srv__ArmSafetyService_Request__rosidl_typesupport_introspection_c__resize_function__ArmSafetyService_Request__positions(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__double__Sequence * member =
    (rosidl_runtime_c__double__Sequence *)(untyped_member);
  rosidl_runtime_c__double__Sequence__fini(member);
  return rosidl_runtime_c__double__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember safety_msgs__srv__ArmSafetyService_Request__rosidl_typesupport_introspection_c__ArmSafetyService_Request_message_member_array[6] = {
  {
    "motion_type",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(safety_msgs__srv__ArmSafetyService_Request, motion_type),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "positions",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(safety_msgs__srv__ArmSafetyService_Request, positions),  // bytes offset in struct
    NULL,  // default value
    safety_msgs__srv__ArmSafetyService_Request__rosidl_typesupport_introspection_c__size_function__ArmSafetyService_Request__positions,  // size() function pointer
    safety_msgs__srv__ArmSafetyService_Request__rosidl_typesupport_introspection_c__get_const_function__ArmSafetyService_Request__positions,  // get_const(index) function pointer
    safety_msgs__srv__ArmSafetyService_Request__rosidl_typesupport_introspection_c__get_function__ArmSafetyService_Request__positions,  // get(index) function pointer
    safety_msgs__srv__ArmSafetyService_Request__rosidl_typesupport_introspection_c__fetch_function__ArmSafetyService_Request__positions,  // fetch(index, &value) function pointer
    safety_msgs__srv__ArmSafetyService_Request__rosidl_typesupport_introspection_c__assign_function__ArmSafetyService_Request__positions,  // assign(index, value) function pointer
    safety_msgs__srv__ArmSafetyService_Request__rosidl_typesupport_introspection_c__resize_function__ArmSafetyService_Request__positions  // resize(index) function pointer
  },
  {
    "velocity",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(safety_msgs__srv__ArmSafetyService_Request, velocity),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "acc_time",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(safety_msgs__srv__ArmSafetyService_Request, acc_time),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "blend_percentage",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(safety_msgs__srv__ArmSafetyService_Request, blend_percentage),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "fine_goal",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(safety_msgs__srv__ArmSafetyService_Request, fine_goal),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers safety_msgs__srv__ArmSafetyService_Request__rosidl_typesupport_introspection_c__ArmSafetyService_Request_message_members = {
  "safety_msgs__srv",  // message namespace
  "ArmSafetyService_Request",  // message name
  6,  // number of fields
  sizeof(safety_msgs__srv__ArmSafetyService_Request),
  safety_msgs__srv__ArmSafetyService_Request__rosidl_typesupport_introspection_c__ArmSafetyService_Request_message_member_array,  // message members
  safety_msgs__srv__ArmSafetyService_Request__rosidl_typesupport_introspection_c__ArmSafetyService_Request_init_function,  // function to initialize message memory (memory has to be allocated)
  safety_msgs__srv__ArmSafetyService_Request__rosidl_typesupport_introspection_c__ArmSafetyService_Request_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t safety_msgs__srv__ArmSafetyService_Request__rosidl_typesupport_introspection_c__ArmSafetyService_Request_message_type_support_handle = {
  0,
  &safety_msgs__srv__ArmSafetyService_Request__rosidl_typesupport_introspection_c__ArmSafetyService_Request_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_safety_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, safety_msgs, srv, ArmSafetyService_Request)() {
  if (!safety_msgs__srv__ArmSafetyService_Request__rosidl_typesupport_introspection_c__ArmSafetyService_Request_message_type_support_handle.typesupport_identifier) {
    safety_msgs__srv__ArmSafetyService_Request__rosidl_typesupport_introspection_c__ArmSafetyService_Request_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &safety_msgs__srv__ArmSafetyService_Request__rosidl_typesupport_introspection_c__ArmSafetyService_Request_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include <stddef.h>
// already included above
// #include "safety_msgs/srv/detail/arm_safety_service__rosidl_typesupport_introspection_c.h"
// already included above
// #include "safety_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "safety_msgs/srv/detail/arm_safety_service__functions.h"
// already included above
// #include "safety_msgs/srv/detail/arm_safety_service__struct.h"


#ifdef __cplusplus
extern "C"
{
#endif

void safety_msgs__srv__ArmSafetyService_Response__rosidl_typesupport_introspection_c__ArmSafetyService_Response_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  safety_msgs__srv__ArmSafetyService_Response__init(message_memory);
}

void safety_msgs__srv__ArmSafetyService_Response__rosidl_typesupport_introspection_c__ArmSafetyService_Response_fini_function(void * message_memory)
{
  safety_msgs__srv__ArmSafetyService_Response__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember safety_msgs__srv__ArmSafetyService_Response__rosidl_typesupport_introspection_c__ArmSafetyService_Response_message_member_array[1] = {
  {
    "ok",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(safety_msgs__srv__ArmSafetyService_Response, ok),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers safety_msgs__srv__ArmSafetyService_Response__rosidl_typesupport_introspection_c__ArmSafetyService_Response_message_members = {
  "safety_msgs__srv",  // message namespace
  "ArmSafetyService_Response",  // message name
  1,  // number of fields
  sizeof(safety_msgs__srv__ArmSafetyService_Response),
  safety_msgs__srv__ArmSafetyService_Response__rosidl_typesupport_introspection_c__ArmSafetyService_Response_message_member_array,  // message members
  safety_msgs__srv__ArmSafetyService_Response__rosidl_typesupport_introspection_c__ArmSafetyService_Response_init_function,  // function to initialize message memory (memory has to be allocated)
  safety_msgs__srv__ArmSafetyService_Response__rosidl_typesupport_introspection_c__ArmSafetyService_Response_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t safety_msgs__srv__ArmSafetyService_Response__rosidl_typesupport_introspection_c__ArmSafetyService_Response_message_type_support_handle = {
  0,
  &safety_msgs__srv__ArmSafetyService_Response__rosidl_typesupport_introspection_c__ArmSafetyService_Response_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_safety_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, safety_msgs, srv, ArmSafetyService_Response)() {
  if (!safety_msgs__srv__ArmSafetyService_Response__rosidl_typesupport_introspection_c__ArmSafetyService_Response_message_type_support_handle.typesupport_identifier) {
    safety_msgs__srv__ArmSafetyService_Response__rosidl_typesupport_introspection_c__ArmSafetyService_Response_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &safety_msgs__srv__ArmSafetyService_Response__rosidl_typesupport_introspection_c__ArmSafetyService_Response_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

#include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "safety_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "safety_msgs/srv/detail/arm_safety_service__rosidl_typesupport_introspection_c.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/service_introspection.h"

// this is intentionally not const to allow initialization later to prevent an initialization race
static rosidl_typesupport_introspection_c__ServiceMembers safety_msgs__srv__detail__arm_safety_service__rosidl_typesupport_introspection_c__ArmSafetyService_service_members = {
  "safety_msgs__srv",  // service namespace
  "ArmSafetyService",  // service name
  // these two fields are initialized below on the first access
  NULL,  // request message
  // safety_msgs__srv__detail__arm_safety_service__rosidl_typesupport_introspection_c__ArmSafetyService_Request_message_type_support_handle,
  NULL  // response message
  // safety_msgs__srv__detail__arm_safety_service__rosidl_typesupport_introspection_c__ArmSafetyService_Response_message_type_support_handle
};

static rosidl_service_type_support_t safety_msgs__srv__detail__arm_safety_service__rosidl_typesupport_introspection_c__ArmSafetyService_service_type_support_handle = {
  0,
  &safety_msgs__srv__detail__arm_safety_service__rosidl_typesupport_introspection_c__ArmSafetyService_service_members,
  get_service_typesupport_handle_function,
};

// Forward declaration of request/response type support functions
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, safety_msgs, srv, ArmSafetyService_Request)();

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, safety_msgs, srv, ArmSafetyService_Response)();

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_safety_msgs
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_c, safety_msgs, srv, ArmSafetyService)() {
  if (!safety_msgs__srv__detail__arm_safety_service__rosidl_typesupport_introspection_c__ArmSafetyService_service_type_support_handle.typesupport_identifier) {
    safety_msgs__srv__detail__arm_safety_service__rosidl_typesupport_introspection_c__ArmSafetyService_service_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  rosidl_typesupport_introspection_c__ServiceMembers * service_members =
    (rosidl_typesupport_introspection_c__ServiceMembers *)safety_msgs__srv__detail__arm_safety_service__rosidl_typesupport_introspection_c__ArmSafetyService_service_type_support_handle.data;

  if (!service_members->request_members_) {
    service_members->request_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, safety_msgs, srv, ArmSafetyService_Request)()->data;
  }
  if (!service_members->response_members_) {
    service_members->response_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, safety_msgs, srv, ArmSafetyService_Response)()->data;
  }

  return &safety_msgs__srv__detail__arm_safety_service__rosidl_typesupport_introspection_c__ArmSafetyService_service_type_support_handle;
}

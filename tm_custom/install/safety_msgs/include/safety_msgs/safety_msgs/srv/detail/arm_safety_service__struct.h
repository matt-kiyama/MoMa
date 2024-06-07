// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from safety_msgs:srv/ArmSafetyService.idl
// generated code does not contain a copyright notice

#ifndef SAFETY_MSGS__SRV__DETAIL__ARM_SAFETY_SERVICE__STRUCT_H_
#define SAFETY_MSGS__SRV__DETAIL__ARM_SAFETY_SERVICE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Constant 'PTP_J'.
enum
{
  safety_msgs__srv__ArmSafetyService_Request__PTP_J = 1
};

/// Constant 'PTP_T'.
enum
{
  safety_msgs__srv__ArmSafetyService_Request__PTP_T = 2
};

/// Constant 'LINE_T'.
/**
  * int8 LINE_J = 3
 */
enum
{
  safety_msgs__srv__ArmSafetyService_Request__LINE_T = 4
};

/// Constant 'CIRC_T'.
/**
  * int8 CIRC_J = 5
 */
enum
{
  safety_msgs__srv__ArmSafetyService_Request__CIRC_T = 6
};

/// Constant 'PLINE_T'.
/**
  * int8 PLINE_J = 7
 */
enum
{
  safety_msgs__srv__ArmSafetyService_Request__PLINE_T = 8
};

// Include directives for member types
// Member 'positions'
#include "rosidl_runtime_c/primitives_sequence.h"

/// Struct defined in srv/ArmSafetyService in the package safety_msgs.
typedef struct safety_msgs__srv__ArmSafetyService_Request
{
  int8_t motion_type;
  rosidl_runtime_c__double__Sequence positions;
  /// motion velocity: if expressed in Cartesian coordinate (unit: m/s) , if expressed in joint velocity (unit: rad/s, and the maximum value is limited to pi )
  double velocity;
  /// time to reach maximum speed (unit: ms)
  double acc_time;
  /// blending value: expressed as a percentage (unit: %, and the minimum value of 0 means no blending)
  int32_t blend_percentage;
  /// precise position mode : If activated, the amount of error in the final position will converge more.
  bool fine_goal;
} safety_msgs__srv__ArmSafetyService_Request;

// Struct for a sequence of safety_msgs__srv__ArmSafetyService_Request.
typedef struct safety_msgs__srv__ArmSafetyService_Request__Sequence
{
  safety_msgs__srv__ArmSafetyService_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} safety_msgs__srv__ArmSafetyService_Request__Sequence;


// Constants defined in the message

/// Struct defined in srv/ArmSafetyService in the package safety_msgs.
typedef struct safety_msgs__srv__ArmSafetyService_Response
{
  bool ok;
} safety_msgs__srv__ArmSafetyService_Response;

// Struct for a sequence of safety_msgs__srv__ArmSafetyService_Response.
typedef struct safety_msgs__srv__ArmSafetyService_Response__Sequence
{
  safety_msgs__srv__ArmSafetyService_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} safety_msgs__srv__ArmSafetyService_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SAFETY_MSGS__SRV__DETAIL__ARM_SAFETY_SERVICE__STRUCT_H_

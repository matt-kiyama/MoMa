// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from safety_msgs:srv/ArmSafetyService.idl
// generated code does not contain a copyright notice

#ifndef SAFETY_MSGS__SRV__DETAIL__ARM_SAFETY_SERVICE__FUNCTIONS_H_
#define SAFETY_MSGS__SRV__DETAIL__ARM_SAFETY_SERVICE__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "safety_msgs/msg/rosidl_generator_c__visibility_control.h"

#include "safety_msgs/srv/detail/arm_safety_service__struct.h"

/// Initialize srv/ArmSafetyService message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * safety_msgs__srv__ArmSafetyService_Request
 * )) before or use
 * safety_msgs__srv__ArmSafetyService_Request__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_safety_msgs
bool
safety_msgs__srv__ArmSafetyService_Request__init(safety_msgs__srv__ArmSafetyService_Request * msg);

/// Finalize srv/ArmSafetyService message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_safety_msgs
void
safety_msgs__srv__ArmSafetyService_Request__fini(safety_msgs__srv__ArmSafetyService_Request * msg);

/// Create srv/ArmSafetyService message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * safety_msgs__srv__ArmSafetyService_Request__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_safety_msgs
safety_msgs__srv__ArmSafetyService_Request *
safety_msgs__srv__ArmSafetyService_Request__create();

/// Destroy srv/ArmSafetyService message.
/**
 * It calls
 * safety_msgs__srv__ArmSafetyService_Request__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_safety_msgs
void
safety_msgs__srv__ArmSafetyService_Request__destroy(safety_msgs__srv__ArmSafetyService_Request * msg);

/// Check for srv/ArmSafetyService message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_safety_msgs
bool
safety_msgs__srv__ArmSafetyService_Request__are_equal(const safety_msgs__srv__ArmSafetyService_Request * lhs, const safety_msgs__srv__ArmSafetyService_Request * rhs);

/// Copy a srv/ArmSafetyService message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_safety_msgs
bool
safety_msgs__srv__ArmSafetyService_Request__copy(
  const safety_msgs__srv__ArmSafetyService_Request * input,
  safety_msgs__srv__ArmSafetyService_Request * output);

/// Initialize array of srv/ArmSafetyService messages.
/**
 * It allocates the memory for the number of elements and calls
 * safety_msgs__srv__ArmSafetyService_Request__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_safety_msgs
bool
safety_msgs__srv__ArmSafetyService_Request__Sequence__init(safety_msgs__srv__ArmSafetyService_Request__Sequence * array, size_t size);

/// Finalize array of srv/ArmSafetyService messages.
/**
 * It calls
 * safety_msgs__srv__ArmSafetyService_Request__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_safety_msgs
void
safety_msgs__srv__ArmSafetyService_Request__Sequence__fini(safety_msgs__srv__ArmSafetyService_Request__Sequence * array);

/// Create array of srv/ArmSafetyService messages.
/**
 * It allocates the memory for the array and calls
 * safety_msgs__srv__ArmSafetyService_Request__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_safety_msgs
safety_msgs__srv__ArmSafetyService_Request__Sequence *
safety_msgs__srv__ArmSafetyService_Request__Sequence__create(size_t size);

/// Destroy array of srv/ArmSafetyService messages.
/**
 * It calls
 * safety_msgs__srv__ArmSafetyService_Request__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_safety_msgs
void
safety_msgs__srv__ArmSafetyService_Request__Sequence__destroy(safety_msgs__srv__ArmSafetyService_Request__Sequence * array);

/// Check for srv/ArmSafetyService message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_safety_msgs
bool
safety_msgs__srv__ArmSafetyService_Request__Sequence__are_equal(const safety_msgs__srv__ArmSafetyService_Request__Sequence * lhs, const safety_msgs__srv__ArmSafetyService_Request__Sequence * rhs);

/// Copy an array of srv/ArmSafetyService messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_safety_msgs
bool
safety_msgs__srv__ArmSafetyService_Request__Sequence__copy(
  const safety_msgs__srv__ArmSafetyService_Request__Sequence * input,
  safety_msgs__srv__ArmSafetyService_Request__Sequence * output);

/// Initialize srv/ArmSafetyService message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * safety_msgs__srv__ArmSafetyService_Response
 * )) before or use
 * safety_msgs__srv__ArmSafetyService_Response__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_safety_msgs
bool
safety_msgs__srv__ArmSafetyService_Response__init(safety_msgs__srv__ArmSafetyService_Response * msg);

/// Finalize srv/ArmSafetyService message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_safety_msgs
void
safety_msgs__srv__ArmSafetyService_Response__fini(safety_msgs__srv__ArmSafetyService_Response * msg);

/// Create srv/ArmSafetyService message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * safety_msgs__srv__ArmSafetyService_Response__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_safety_msgs
safety_msgs__srv__ArmSafetyService_Response *
safety_msgs__srv__ArmSafetyService_Response__create();

/// Destroy srv/ArmSafetyService message.
/**
 * It calls
 * safety_msgs__srv__ArmSafetyService_Response__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_safety_msgs
void
safety_msgs__srv__ArmSafetyService_Response__destroy(safety_msgs__srv__ArmSafetyService_Response * msg);

/// Check for srv/ArmSafetyService message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_safety_msgs
bool
safety_msgs__srv__ArmSafetyService_Response__are_equal(const safety_msgs__srv__ArmSafetyService_Response * lhs, const safety_msgs__srv__ArmSafetyService_Response * rhs);

/// Copy a srv/ArmSafetyService message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_safety_msgs
bool
safety_msgs__srv__ArmSafetyService_Response__copy(
  const safety_msgs__srv__ArmSafetyService_Response * input,
  safety_msgs__srv__ArmSafetyService_Response * output);

/// Initialize array of srv/ArmSafetyService messages.
/**
 * It allocates the memory for the number of elements and calls
 * safety_msgs__srv__ArmSafetyService_Response__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_safety_msgs
bool
safety_msgs__srv__ArmSafetyService_Response__Sequence__init(safety_msgs__srv__ArmSafetyService_Response__Sequence * array, size_t size);

/// Finalize array of srv/ArmSafetyService messages.
/**
 * It calls
 * safety_msgs__srv__ArmSafetyService_Response__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_safety_msgs
void
safety_msgs__srv__ArmSafetyService_Response__Sequence__fini(safety_msgs__srv__ArmSafetyService_Response__Sequence * array);

/// Create array of srv/ArmSafetyService messages.
/**
 * It allocates the memory for the array and calls
 * safety_msgs__srv__ArmSafetyService_Response__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_safety_msgs
safety_msgs__srv__ArmSafetyService_Response__Sequence *
safety_msgs__srv__ArmSafetyService_Response__Sequence__create(size_t size);

/// Destroy array of srv/ArmSafetyService messages.
/**
 * It calls
 * safety_msgs__srv__ArmSafetyService_Response__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_safety_msgs
void
safety_msgs__srv__ArmSafetyService_Response__Sequence__destroy(safety_msgs__srv__ArmSafetyService_Response__Sequence * array);

/// Check for srv/ArmSafetyService message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_safety_msgs
bool
safety_msgs__srv__ArmSafetyService_Response__Sequence__are_equal(const safety_msgs__srv__ArmSafetyService_Response__Sequence * lhs, const safety_msgs__srv__ArmSafetyService_Response__Sequence * rhs);

/// Copy an array of srv/ArmSafetyService messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_safety_msgs
bool
safety_msgs__srv__ArmSafetyService_Response__Sequence__copy(
  const safety_msgs__srv__ArmSafetyService_Response__Sequence * input,
  safety_msgs__srv__ArmSafetyService_Response__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // SAFETY_MSGS__SRV__DETAIL__ARM_SAFETY_SERVICE__FUNCTIONS_H_

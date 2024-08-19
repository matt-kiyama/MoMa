std_msgs/Header header

int8 motion_type
float64[] positions
float64 velocity       # motion velocity: if expressed in Cartesian coordinate (unit: m/s) , if expressed in joint velocity (unit: rad/s, and the maximum value is limited to pi )
float64 acc_time       # time to reach maximum speed (unit: ms)
int32 blend_percentage # blending value: expressed as a percentage (unit: %, and the minimum value of 0 means no blending)
bool fine_goal         # precise position mode : If activated, the amount of error in the final position will converge more.
---
# ok :  set motion status 
bool ok

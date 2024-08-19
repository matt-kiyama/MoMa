import math

def is_valid_angle(joint_pos, min, max):
    if joint_pos < min or joint_pos > max:
        return False
    else:
        return True

def is_valid_velocity(velocity, min, max):
    if velocity < min or velocity > max:
        return False
    else:
        return True
    
def check_joint_angles(safetyNode, angle_list):
    #print("angle_list: ")
    #print(angle_list)
    error_tuple = (0, True)
    #print(safetyNode.joint_thresholds.items())
    for key, (value1, value2) in safetyNode.joint_thresholds.items():
        #print(f"Key: {key}, Max: {value1}, Min: {value2}")
        min_element = value1
        max_element = value2
        position_in_deg = math.degrees(angle_list[int(key)])
        #print(position_in_deg)
        if is_valid_angle(position_in_deg, min_element, max_element) == False:
            error_tuple = (int(key), False)
            return error_tuple
    return error_tuple


def check_base_speed(safetyNode, odom_msg):
    
    for key, (value1, value2) in safetyNode.base_thresholds.items():
        #print(f"Key: {key}, Max: {value1}, Min: {value2}")
        min_element = value1
        max_element = value2

        error_tuple = ('none', True)
        match key:
            case 'x_linear':
                if is_valid_velocity(odom_msg.twist.twist.linear.x, min_element, max_element) == False:
                    error_tuple = (key, False)
                    return error_tuple
                else:
                    print('x_linear good')
            case 'y_linear':
                if is_valid_velocity(odom_msg.twist.twist.linear.y, min_element, max_element) == False:
                    error_tuple = (key, False)
                    return error_tuple
                else:
                    print('y_linear good')
            case 'z_linear':
                if is_valid_velocity(odom_msg.twist.twist.linear.z, min_element, max_element) == False:
                    error_tuple = (key, False)
                    return error_tuple
                else:
                    print('z_linear good')
            case _:
                return error_tuple
    

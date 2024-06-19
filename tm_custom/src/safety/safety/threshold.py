import math

def is_valid_angle(joint_pos, min, max):
    if joint_pos < min or joint_pos > max:
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



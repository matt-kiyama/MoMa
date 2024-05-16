import math


#isValidAngle
#checkAllAngles


def convert_angle(angle, to_degrees):
    """Convert angle between radians and degrees."""
    if to_degrees:
        return angle * (180.0 / math.pi)
    else:
        return angle * (math.pi / 180.0)
    

def is_valid_angle(joint_pos, min, max):
    if joint_pos < min or joint_pos > max:
        return False
    else:
        return True
    
def check_joint_angles(safetyNode, msg):
    error_tuple = (0, True)
    for key, value in safetyNode.joint_thresholds:
        print(f"Key: {key}, Tuple: {value}")
        min_element = value[0]
        max_element = value[1]
        if is_valid_angle(msg.joint_pos[int(key)],min_element, max_element) == False:
            error_tuple = (int(key), False)
            return error_tuple
    return error_tuple



import math


def convert_angle(angle, to_degrees):
    """Convert angle between radians and degrees."""
    if to_degrees:
        return angle * (180.0 / math.pi)
    else:
        return angle * (math.pi / 180.0)
    

def joint_thresholds_angle(safetyNode, msg):
    if msg.joint_pos[0] < -10 or msg.joint_pos[0] > 100:
        safetyNode.lock = False
    else:
        safetyNode.lock = True
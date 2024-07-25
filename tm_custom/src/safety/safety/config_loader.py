import yaml
import numpy as np
from safety_node import *

def read_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def create_dict_of_tuples(yaml_file):
    yaml_data = read_yaml(yaml_file)
    dict_of_tuples = {}
    for key, value in yaml_data.items():
        if isinstance(value, list) and len(value) == 2:
            dict_of_tuples[key] = tuple(value)
    return dict_of_tuples

def yaml_to_np_array(yaml_file):
    yaml_data = read_yaml(yaml_file)
    data_list = []
    for key, value in yaml_data.items():
        if isinstance(value, list) and len(value) == 1:
            data_list.append(value[0])
    np_array = np.array(data_list)
    return np_array

def load_base_thresholds_from_yaml(file_path: str) -> Mobile_Manipulator_Base_Thresholds:
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

    return Mobile_Manipulator_Base_Thresholds(
        x_linear_min=data['x_linear'][0],
        x_linear_max=data['x_linear'][1],
        y_linear_min=data['y_linear'][0],
        y_linear_max=data['y_linear'][1],
        z_linear_min=data['z_linear'][0],
        z_linear_max=data['z_linear'][1],
        x_angular_min=data['x_angular'][0],
        x_angular_max=data['x_angular'][1],
        y_angular_min=data['y_angular'][0],
        y_angular_max=data['y_angular'][1],
        z_angular_min=data['z_angular'][0],
        z_angular_max=data['z_angular'][1]
    )

def load_arm_thresholds_from_yaml(file_path: str) -> Mobile_Manipulator_Arm_Thresholds:
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

    joint_thresholds = Mobile_Manipulator_Arm_Thresholds.JointThresholds(
        joint_1_min=data['joint_1'][0],
        joint_1_max=data['joint_1'][1],
        joint_2_min=data['joint_2'][0],
        joint_2_max=data['joint_2'][1],
        joint_3_min=data['joint_3'][0],
        joint_3_max=data['joint_3'][1],
        joint_4_min=data['joint_4'][0],
        joint_4_max=data['joint_4'][1],
        joint_5_min=data['joint_5'][0],
        joint_5_max=data['joint_5'][1],
        joint_6_min=data['joint_6'][0],
        joint_6_max=data['joint_6'][1]
    )

    xyz_thresholds = Mobile_Manipulator_Arm_Thresholds.XYZThresholds(
        x_min=(data['x_range'][0]) / 1000.0,
        x_max=(data['x_range'][1]) / 1000.0,
        y_min=(data['y_range'][0]) / 1000.0,
        y_max=(data['y_range'][1]) / 1000.0,
        z_min=(data['z_range'][0]) / 1000.0,
        z_max=(data['z_range'][1]) / 1000.0
    )

    velocity_thresholds = Mobile_Manipulator_Arm_Thresholds.VelocityThresholds(
        joint_velocity=data['joint_vel'][0],
        tcp_velocity=data['tcp_vel'][0]
    )

    return Mobile_Manipulator_Arm_Thresholds(
        joint_thresholds=joint_thresholds,
        xyz_thresholds=xyz_thresholds,
        velocity_thresholds=velocity_thresholds
    )

if __name__ == "__main__":
    # Read the YAML file
    yaml_file = 'arm_thresholds.yaml'
    
    # Create the dictionary of tuples
    result = create_dict_of_tuples(yaml_file)

    # Print the result
    print(result)
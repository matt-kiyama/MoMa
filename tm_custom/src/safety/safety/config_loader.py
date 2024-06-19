import yaml

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


if __name__ == "__main__":
    # Read the YAML file
    yaml_file = 'arm_thresholds.yaml'
    
    # Create the dictionary of tuples
    result = create_dict_of_tuples(yaml_file)

    # Print the result
    print(result)
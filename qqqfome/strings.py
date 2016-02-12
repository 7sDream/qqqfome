import os
import json

file_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(file_dir, 'config.json')

assert os.path.isfile(config_file_path)

with open(config_file_path, 'r', encoding='utf-8') as f:
    json_string = f.read()
    json_dict = json.loads(json_string)
    for k, v in json_dict.items():
        exec(k + " = '" + v + "'")

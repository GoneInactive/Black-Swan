import sys
import os
import yaml

def load_settings(param="program.name"):
    #param = sys.argv[1]
    base_dir = os.path.dirname(os.path.abspath(__file__))
    settings_path = os.path.join(base_dir, '..', '..', 'config', 'settings', 'settings.yaml')

    with open(settings_path, 'r') as f:
        settings = yaml.safe_load(f)

    key = param.split('.')[0]
    value = param.split('.')[1]

    if value == "*":
        return settings.get(key)
    
    return settings.get(key).get(value)
    # else:
    #     print(settings)
    #     print(settings.keys())
    #     print(settings.values())
    #     print(settings.items())
    #     print(settings.get(param))
    #     print(settings.get(param.split('.')[0]))
    #     print(settings.get(param.split('.')[0]).get(param.split('.')[1]))
    #     print(settings.get(key))
    #     print(settings.get(key).get(value))
    #     print('-'*100)
    #     return None
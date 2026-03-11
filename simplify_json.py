import os 
import json

directory = 'json_files'
for entry in os.scandir(directory):  
    if entry.is_file():
        file_name = os.path.basename(entry)
        with open(entry, 'r') as f:
            data = json.load(f)
            new_json = data
            for key, value in new_json.items():
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            for name in item:
                                if name=='Instance':
                                    instances = item['Instance']
                                    replacement_dic = {}
                                    if "NONE" not in instances and 'None' not in instances:
                                        for instance in instances:
                                            new_key = f"{key}[{instance}]"
                                            new_val = {k: v for k, v in item.items() if k != "Instance"}
                                            replacement_dic.update({new_key: new_val})
                                        new_json[key] = replacement_dic
                                        print(replacement_dic)




import os 
import json

directory = 'json_files'
new_folder = 'simple_json_files'
os.makedirs(new_folder, exist_ok=True)
for entry in os.scandir(directory):  
    if entry.is_file():
        file_name = os.path.basename(entry)
        with open(entry, 'r') as f:
            data = json.load(f)
            new_json = data
            for key, value in list(new_json.items()):
                change = False
                if isinstance(value, list):
                    replacement_dic = {}
                    for item in value:
                        if isinstance(item, dict):
                            for name in item:
                                if name=='Instance':
                                    instances = item['Instance']
                                    if "NONE" not in instances and 'None' not in instances:
                                        for instance in instances:
                                            new_key = f"{key}[{instance}]"
                                            new_val = {k: v for k, v in item.items() if k != "Instance"}
                                            replacement_dic[new_key] = new_val
                                            new_json.update(replacement_dic)
                                            change = True

                                if name=='Modifications':
                                    for mod_item in item[name]: #going through items in the nested dictionary in 'Modifications'
                                        print(mod_item)
                                        if mod_item['Frequency']=="":
                                            mod_item['Frequency'] = ['Total']
                    if change==True:
                        del new_json[key]
            output_path = os.path.join(new_folder, "new"+entry.name)
            with open(output_path, 'w') as f:
                json.dump(new_json, f, indent=4)




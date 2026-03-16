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
                replace_lh = {}
                change = False

                if 'L1H1' in key:
                    new_key = key.replace('L1H1', 'LH')
                    replace_lh[new_key] = value
                    new_json.update(replace_lh)
                    del new_json[key]
                    key = new_key
                if 'L2H2' in key:
                    new_key = key.replace('L2H2', 'LH')
                    replace_lh[new_key] = value
                    new_json.update(replace_lh)
                    del new_json[key]
                    key = new_key


                if isinstance(value, list):

                    replacement_dic = {}
                    for item in value:
                        if isinstance(item, dict):
                            instance_present = False
                            for name in item:
                                if name=='Instance':
                                    instance_present = True
                                    instances = item['Instance']
                                    if "NONE" not in instances and 'None' not in instances:
                                        for instance in instances:
                                            new_key = f"{key}[{instance}]"
                                            if 'Length' in key:
                                                new_val = item['Values'][0]
                                            else:
                                                new_val = {k: v for k, v in item.items() if k != "Instance"}
                                            replacement_dic[new_key] = new_val
                                            new_json.pop(key, None)
                                            new_json.update(replacement_dic)
                                    else:
                                        for thing in name:
                                            new_key = f"{key}[0]"
                                            new_val = {k: v for k, v in item.items()}
                                            replacement_dic[new_key] = new_val
                                            new_json.pop(key, None)
                                            new_json.update(replacement_dic)


                                if name=='Modifications':
                                    for mod_item in item[name]: #going through items in the nested dictionary in 'Modifications'
                                        if mod_item['Frequency']=="":
                                            mod_item['Frequency'] = ['Total']

                                if instance_present == False:
                                    for thing in name:
                                        new_key = f"{key}[0]"
                                        new_val = new_val = {k: v for k, v in item.items()}
                                        replacement_dic[new_key] = new_val
                                        new_json.pop(key, None)
                                        new_json.update(replacement_dic)




            output_path = os.path.join(new_folder, "new"+entry.name)
            with open(output_path, 'w') as f:
                json.dump(new_json, f, indent=4)




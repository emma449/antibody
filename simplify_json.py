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
                                                new_val = [item['Values'][0]] #change the nested dictionary into single dictionary
                                            else:
                                                new_val = {k: v for k, v in item.items() if k != "Instance"}

                                            replacement_dic[new_key] = new_val

                                            if 'Potential' in item:
                                                if item['Potential'] == ["None"] or item['Potential']==['NONE']:
                                                    replacement_dic[f'{new_key}Potential'] = [0]
                                                else:
                                                    replacement_dic[f'{new_key}Potential'] = item['Potential']
                                                replacement_dic.pop(new_key, None)

                                            if 'Confirmed' in item:
                                                if item['Confirmed'] == ['None'] or item['Confirmed']==['NONE']:
                                                    replacement_dic[f'{new_key}Confirmed'] = [0]
                                                else:
                                                    replacement_dic[f'{new_key}Confirmed'] = item['Confirmed']
                                                replacement_dic.pop(new_key, None)

                                            if 'Modifications' in item:
                                                for mod_item in item['Modifications']:
                                                    mod_key = mod_item['Type']

                                                    if mod_item['Frequency'] == '':
                                                        mod_item['Frequency'] = ['Total']

                                                    mod_val = {k: v for k, v in mod_item.items() if k != 'Type'}
                                                    replacement_dic.pop(new_key, None)
                                                    replacement_dic[mod_key] = mod_val


                                            new_json.pop(key, None)
                                            new_json.update(replacement_dic)
                                    else:
                                        new_key = f"{key}[0]"
                                        new_val = {k: v for k, v in item.items()}
                                        replacement_dic[new_key] = new_val
                                        if 'Modifications' in item:
                                            for mod_item in item['Modifications']:
                                                mod_key = mod_item['Type']

                                                if mod_item['Frequency'] == '':
                                                    mod_item['Frequency'] = ['Total']

                                                mod_val = {k: v for k, v in mod_item.items() if k != 'Type'}
                                                replacement_dic.pop(new_key, None)
                                                replacement_dic[mod_key] = mod_val

                                        new_json.pop(key, None)
                                        new_json.update(replacement_dic)




                                    if name=='Modifications':
                                            item[name]['Frequency'] = ['Total']




                                if instance_present == False:
                                    new_key = f"{key}[0]"
                                    new_val = new_val = {k: v for k, v in item.items()}
                                    replacement_dic[new_key] = new_val
                                    new_json.pop(key, None)
                                    new_json.update(replacement_dic)





            output_path = os.path.join(new_folder, "new"+entry.name)
            with open(output_path, 'w') as f:
                json.dump(new_json, f, indent=4)




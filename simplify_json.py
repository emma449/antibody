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

                if 'DisulfidesIntra' in key and 'Note' not in key:
                    if isinstance(value, str):

                        new_value = {'Instance': [0], 'Values': value.split()}
                        replace_lh[key] = new_value
                        value = new_value

                                                
                    else:
                        new_value = value if isinstance(value, list) else value.split()
                        replace_lh[key] = new_value
                        new_json.update(replace_lh)
                    disulfides_list = []
                    for bond_item in value:
                        if isinstance(bond_item, dict) and isinstance(bond_item['Values'], str):
                            bonds = bond_item['Values'].replace("-", " ").split()
                        elif isinstance(bond_item, dict):
                            print(f'list bond_item: {bond_item}')
                            bonds = bond_item['Values']
                        else:
                            print(bond_item)
                            bonds = bond_item.replace("-", " ").split()
                        for i in range(len(bonds)-1):
                            residue = bonds[i]
                            partner = bonds[i+1]
                            disulfides_list.append({'Residue': [residue], 'PartnerResidue': [partner], 'PartnerInstance': instances})
                    value = disulfides_list
                    new_json.update({key: disulfides_list})

                if 'Positions' in key:
                    new_value = value if isinstance(value, list) else value.split()
                    replace_lh[key] = new_value
                    new_json.update(replace_lh)



                if isinstance(value, list):

                    replacement_dic = {}
                    for item in value:
                        if isinstance(item, dict):
                            instance_present = False
                            for name in item:

                                if 'Instance' in name:
                                    instance_present = True
                                    if name=='InstanceA':
                                        instances = [item['InstanceA']]
                                        for instance_a in instances:
                                            if str(instance_a).upper() =='NONE':
                                                instance_a = 0
                                            new_key = f'{key}[{instance_a}]'
                                            if len(item['Bonds'])==0:
                                                bonds = item['Bonds'][0]['A']
                                                partner = item['InstanceB']
                                                if partner == 'NONE':
                                                    partner = 0
                                                if 'LH' in key:
                                                    if bonds>item['Bonds'][0]['B']:
                                                        ThisChain = 'H'
                                                        HResidue = bonds
                                                        LResidue = item['Bonds'][0]['B']
                                                    else:
                                                        ThisChain= 'L'
                                                        LResidue = bonds
                                                        HResidue = item['Bonds'][0]['B']
                                                    new_val = [{'HResidue': HResidue, 'LResidue': LResidue, 'Partner': partner, 'ThisChain': ThisChain}]
                                                else:
                                                    new_val = [{'Residue': bonds, 'Partner': partner}]
                                                replacement_dic[new_key] = new_val
                                                new_json.update(replacement_dic)
                                            else:
                                                a_bonds = []
                                                b_bonds = []
                                                for bond in item['Bonds']:
                                                    a_bonds.append(bond['A'])
                                                    b_bonds.append(bond['B'])

                                    elif name=='InstanceB':
                                        instances = [item['InstanceB']]
                                        for instance_b in instances:
                                            if str(instance_b).upper() == 'NONE':
                                                instance_b = 0
                                            new_key = f'{key}[{instance_b}]'
                                            bonds = item['Bonds'][0]['B']
                                            partner = item['InstanceA']
                                            if partner == 'NONE':
                                                partner = 0
                                            if 'LH' in key:
                                                if bonds>item['Bonds'][0]['A']:
                                                    ThisChain = 'H'
                                                    HResidue = bonds
                                                    LResidue = item['Bonds'][0]['A']
                                                else:
                                                    ThisChain= 'L'
                                                    LResidue = bonds
                                                    HResidue = item['Bonds'][0]['A']
                                                new_val = [{'HResidue': HResidue, 'LResidue': LResidue, 'Partner': partner, 'ThisChain': ThisChain}]
                                            else:
                                                new_val = [{'Residue': bonds, 'Partner': partner}]
                                            replacement_dic[new_key] = new_val
                                            new_json.pop(key, None)
                                            new_json.update(replacement_dic)



                                    elif name=='Instance':

                                        instances = item.get('Instance', [0])
                                        if isinstance(instances, str):
                                            if instances.upper() == 'NONE':
                                                instances = [0]
                                            if instances == 'A' or instances == 'B' or instances == 'AB':
                                                instances = [0]



                                        elif isinstance(instances, list):
                                            if all(str(x).upper() == "NONE" for x in instances):
                                                instances = [0]
                                        else:
                                            instances = [instances]
                                        for instance in instances:
                                            if isinstance(instance, str):
                                                instance = int(instance) if instance.isnumeric() else instance
                                            new_key = f"{key}{[instance]}"

                                            if 'Length' in key:
                                                new_val = [item['Values'][0]] #change the nested dictionary into single dictionary
                                            else:
                                                new_val = {k: v for k, v in item.items() if k != "Instance"}

                                            replacement_dic[new_key] = new_val

                                            if 'Potential' in item:
                                                if new_json['Request'] == "12775":
                                                    continue
                                                if item['Potential'] == ["None"] or item['Potential']==['NONE']:
                                                    replacement_dic[f'{new_key}Potential'] = [0]
                                                else:
                                                    replacement_dic[f'{new_key}Potential'] = [int(res.replace(" ", "")) for res in item['Potential']]
                                                replacement_dic.pop(new_key, None)

                                            if 'Confirmed' in item:
                                                if new_json['Request'] == "12775":
                                                    continue
                                                if item['Confirmed'] == ['None'] or item['Confirmed']==['NONE']:
                                                    replacement_dic[f'{new_key}Confirmed'] = [0]
                                                else:
                                                    replacement_dic[f'{new_key}Confirmed'] = [int(res.replace(" ", "")) for res in item['Confirmed']]
                                                replacement_dic.pop(new_key, None)

                                            if 'Modifications' in item:
                                                for mod_item in item['Modifications']:

                                                    if mod_item['Frequency'] == '':
                                                        mod_item['Frequency'] = ['Total']

                                            if 'Values' in item:
                                                value_vals = item['Values']
                                                replacement_dic[new_key] = value_vals
                                            if 'Value' in item:
                                                value_vals = item['Value']
                                                replacement_dic[new_key] = value_vals
                                            if 'value' in item:
                                                value_vals = item['value'].split() #making multiple values that are currently all in one string into an array
                                                replacement_dic[new_key] = value_vals



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
                                    new_val = {k: v for k, v in item.items() if k != "Instance"}
                                    replacement_dic[new_key] = new_val
                                    new_json.pop(key, None)
                                    new_json.update(replacement_dic)



            for k, v in new_json.items():
                if 'DisulfidesIntra' in k and isinstance(v, str):
                    new_json[k] = v.split()

            output_path = os.path.join(new_folder, "new"+entry.name)
            with open(output_path, 'w') as f:
                json.dump(new_json, f, indent=4)




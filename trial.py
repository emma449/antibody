import os 
import json

directory = 'json_files'
new_folder = 'trial_json_files'
os.makedirs(new_folder, exist_ok=True)
for entry in os.scandir(directory): 
	if entry.is_file():
		new_json = {}
		file_name = os.path.basename(entry)
		with open(entry, 'r') as f:
			data = json.load(f)
			if 'Request' not in data:
				continue
			delete_keys = []
			for key, value in data.items():

				if key=='Request':
					request = data['Request']
					continue

				if 'Chain[' in key:
					new_json[key] = value
					continue

				if 'Linker' in key:
					new_json[key] = value
					continue

				if 'Fusion[' in key:
					new_json[key] = data[key]
					continue

				if 'Germline' in key:
					print(value)
					if '[' not in key:
						gene_info_present = False
						genes = []
						if isinstance(value, str):
							species_gene = value
							species_gene = species_gene.split()
							geneid = species_gene[-1]
							species = species_gene[:len(species_gene)-1]
							joined_species = " ".join(species)
							new_json[f'{key}[0]'] = {'Species': joined_species, 'GeneID': geneid}
							continue
						for item in value:
							if 'GeneID' in item:
								geneid = item['GeneID']
								gene_info_present = True
								genes.append(geneid)
							else:
								print(item)
								species_gene = item['Values']
								species_gene = species_gene.split()
								geneid = species_gene[-1]
								species = species_gene[:len(species_gene)-1]
								joined_species = " ".join(species)
								gene_info_present = False
							if 'Instance' in item:
								instance = item['Instance']
								print(file_name)
								if isinstance(instance, list)==False:
									instance = [instance]
								for inst in instance:
									if gene_info_present:
										new_values = {k: v for k, v in item.items() if k != "Instance"}
										new_json[f'{key}[{inst}]'] = new_values
									else:
										new_json[f'{key}[{inst}]'] = {'Species': joined_species, 'GeneID': geneid}
							else:
								if gene_info_present:
									if len(genes)>1:
										if genes[0]!=genes[1]:
											new_values = {k: v for k, v in item.items() if k != "Instance"}
											new_json[f'{key}[0]'] = new_values
								else:
									new_json[f'{key}[0]'] = {'Species': joined_species, 'GeneID': geneid}
						continue
					else:
						new_json[key] = value

				if key == 'Format_Instances_Note':
					format_items = data[key]
					for item in format_items:
						if 'Instance' in item:
							format_instances = item['Instance']
							format_key = f'Format_Note[{format_instances[0]}]'
							del format_instances[0]
							new_values = {'Note': item['Note']}
							new_values['WithInstances']= format_instances
							new_json[format_key] = new_values
					continue

				if 'DisulfidesInter' in key and 'Note' not in key:
					for item in value:
						dic = []
						if 'InstanceA' in item:
							new_key = f'{key}[{item['InstanceA']}]'
							partner_inst = item['InstanceB']
						elif item!= 'InstanceB':
							new_key = f'{key}[0]'
							partner_inst = 0
						if 'Bonds' in item:
							a_bonds = []
							b_bonds = []
							bonds = item['Bonds']
							for bond in bonds:
								a_bonds.append(bond['A'])
								b_bonds.append(bond['B'])
							for i in range (len(a_bonds)):
								thischain = 'H' if ('H' in key and 'L' not in key) else 'L'
								partnerchain = 'L' if ('L' in key and 'H' not in key) else 'H'
								dic.append({'ThisChain': thischain, 'Residue': a_bonds[i], 'PartnerChain': partnerchain, 'PartnerResidue': b_bonds[i], 'PartnerInstance': partner_inst})
							new_json[new_key] = dic
						else:
							instance = 0
							thischain = 'H' if ('H' in key and 'L' not in key) else 'L'
							partnerchain = 'L' if ('L' in key and 'H' not in key) else 'H'
							print(file_name)
							if 'Partner' in item:
								dic.append({'ThisChain': thischain, 'Residue': item['Residue'], 'PartnerChain': partnerchain, 'PartnerResidue': item['PartnerResidue'], 'PartnerInstance': instance})
							else:
								dic.append({'ThisChain': thischain, 'Residue': 0, 'PartnerChain': partnerchain, 'PartnerResidue': 0, 'PartnerInstance': instance})
					continue




				if 'ChainLength' in key:
					new_json[key] = data[key]
					continue

				if key=='Antigen':
					antigen_items = data[key]
					for item in antigen_items:
						if 'Instance' in item:
							antigen_instances = item['Instance']

							antigen_key = f'Antigen[{antigen_instances[0]}]'
							del antigen_instances[0]
							new_values = {k: v for k, v in item.items() if k != "Instance"}
							new_values['WithInstances']= antigen_instances
							new_json[antigen_key] = new_values
					continue

				if isinstance(value, str) and 'ChainClass' not in key and 'Positions' not in key: #for values like request
					new_json[key] = value

				if 'Chain[' in key and ' ' not in key:
					new_json[key] = value

				if 'HeavyChainClass' in key or 'LightChainClass' in key:
					if '[' not in key:
						for item in value:
							if 'Instance' in item:
								instance = [0] if item['Instance']=='NONE' else item['Instance']
								for inst in instance:
									new_key = f'{key}[{inst}]'
									print(item)
									new_json[new_key] = [item['Values']]
							else:
								print(f'no inst val: {value}')
								new_json[f'{key}[0]'] = [value]
						continue
					else:
						new_json[key] = value
					continue

				if 'Heavy Chain' in key:
					new_json[key.replace(" ", "")] = value
					if entry.name == '12318.json':
						print('yes')
						print(new_json[key.replace(" ", "")])
					continue




				if key=='Type':
					type_items = data[key]
					for item in type_items:
						if 'Instance' in item:
							type_instances = item['Instance']
							type_key = f'Type[{type_instances[0]}]'
							del type_instances[0]
							new_values = {'Values': item['Values']}
							new_values['WithInstances']= type_instances
							new_json[type_key] = new_values
					continue


				if 'Range' in key and 'Note' not in key:
					for item in value:
						if 'Instance' in item:
							instance = [0] if item['Instance']=='NONE' else item['Instance']
							for inst in instance:
								info = item
								del info['Instance']
								new_json[f'{key}[{inst}]'] = info
						else:
							instance = [0]
							new_json[f'{key}{instance}'] = item
					continue

				if 'Mutation' in key and 'Note' not in key:
					for item in value:
						if 'Values' in item:
							mutation = item['Values']
							if '(' not in mutation:
								reason = 'No reason given'
								mutations = mutation
							else:
								reason = mutation.split()[-1]
								mutations = item['Values'].split("(", 1)[0].strip().split(" ")
							mutation_dic = [{"Mutation": m, "Reason": reason} for m in mutations]
							if 'Instance' in item:
								instance = [0] if item['Instance']=='NONE' else item['Instance']
								for inst in instance:
									new_json[f'{key}[{inst}]'] = mutation_dic
						elif 'Instance' in item:
							instance = [0] if item['Instance']=='NONE' or item['Instance']=='None' else item['Instance']
							for inst in instance:
								new_json[f'{key}[{inst}]'] = item['Mutations']
						else:
							new_json[f'{key}[0]'] = item['Mutations']
					continue


				if 'DisulfidesIntra' in key:

					chain = 'L' if 'Light' in key else 'H'
					for item in value:
						if 'Instance' in item:
							instance = item['Instance']
							if instance!= 'A' and instance!='B' and instance!='AB' and isinstance(instance, int)==False:
								if ',' in instance:
									instance = instance.replace(',', ' ').split()
									instance = [int(inst) for inst in instance]
							else:
								instance = 0
						else:
							instance = 0
						bond_pairs = []
						disulfides_dic = []
						if 'Values' in item:
							bonds = item['Values'].split() if isinstance(item['Values'], str) else item['Values']
						elif 'Value' in item:
							bonds = item['Value'].split() if isinstance(item['Value'], str) else item['Value']
						else:
							bonds = value.split() if isinstance(value, str) else value


						if len(bonds)==2 and isinstance(bonds[0], int):
							int_pairs = [int(bonds[0]), int(bonds[1])]

						else:

							for bond_pair in bonds:
								pairs = bond_pair.replace("-", " ").split() if isinstance(bond_pair, str) else bond_pair
								if len(pairs)>1:
									int_pairs = [int(pairs[0]), int(pairs[1])]
									bond_pairs.append(int_pairs)
						if isinstance(instance, list):
							if len(instance)==1:
								instance = instance[0]
						if isinstance(instance, list):
							new_key = f'{key}[0]' if instance == [0] else key
							for bond_pair in bond_pairs:
								disulfides_dic.append({'ThisChain': chain, 'Residue': bond_pair[0], 'PartnerChain': chain, 'PartnerResidue': bond_pair[1], 'ParterInstance': int(instance[1])})
								disulfides_dic.append({'ThisChain': chain, 'Residue': bond_pair[1], 'PartnerChain': chain, 'PartnerResidue': bond_pair[0], 'ParterInstance': int(instance[1])})
						else:
							new_key = f'{key}[0]' if instance == [0] else key
							for bond_pair in bond_pairs:
								disulfides_dic.append({'ThisChain': chain, 'Residue': bond_pair[0], 'PartnerChain': chain, 'PartnerResidue': bond_pair[1], 'ParterInstance': int(instance)})
								disulfides_dic.append({'ThisChain': chain, 'Residue': bond_pair[1], 'PartnerChain': chain, 'PartnerResidue': bond_pair[0], 'ParterInstance': int(instance)})
						new_json[new_key] = disulfides_dic

						delete_keys.append(key)

						continue

				if 'Positions' in key and 'Note' not in key:
					if isinstance(value, str):
						values = value.split()
						values = [int(val) for val in values]
						if '[' in key:
							instance = [int(inst) for inst in key.strip().split("[")[1][:-1].split(",")]
							main_key = key.split('[')[0]
						else:
							main_key = key
							instance = [0]
						for inst in instance:
							new_json[f'{main_key}[{inst}]'] = values
						continue
					for item in value:
						if 'Instance' in item:
							instance = [0] if item['Instance'] == 'NONE' else item['Instance']
							instance = [int(i) for i in instance] if isinstance(instance, list) else [instance]
							values = item['Values']
							for inst in instance:
								new_json[f'{key}[{inst}]'] = values
						else:
							print(key, value)
							print(file_name)
							print(item)
							values = item['Values']
							new_json[f'{key}[0]'] = values
					continue

				if key=='Domains':
					for item in value:
						if 'Instance' in item:
							instance = [0] if item['Instance'] == 'NONE' else item['Instance']
							instance = [int(i) for i in instance] if isinstance(instance, list) else [instance]
							values = item['value'].split()
							for inst in instance:
								new_json[f'{key}[{inst}]'] = values
						else:
							values = item['value'].split()
							new_json[f'{key}[0]'] = values
					continue


				if 'Glycos' in key:
					for item in value:
						if 'Potential' in item:
							if 'Instance' in item:
								if item['Instance'] == 'NONE':
									instance = [0]
								else:
									instance = [int(i) for i in item['Instance']]
							else:
								instance = [0]
							for inst in instance:
								glycos_key = f'{key}Potential[{inst}]'
								new_json[glycos_key] = item['Potential']
						if 'Confirmed' in item:
							if 'Instance' in item:
								if item['Instance'] == 'NONE':
									instance = [0]
								else:
									instance = [int(i) for i in item['Instance']]
							else:
								instance = [0]
							for inst in instance:
								glycos_key = f'{key}Confirmed[{inst}]'
								new_json[glycos_key] = item['Confirmed']
						if 'Values' in item:
							if 'Instance' in item:
								if item['Instance'] == 'NONE':
									instance = [0]
								else:
									instance = [int(i) for i in item['Instance']]
							else:
								instance = [0]
							for inst in instance:
								glycos_key = f'{key}[{inst}]'
								values = item['Values'] if item['Values']!='NONE' else ['NONE']
								new_json[glycos_key] = item['Values']
					continue

				if 'HeavyConfirmed' in key or 'LighConfirmed' in key:
					for item in value:
						vals = item
						if 'Instance' in item:
							instance_val = [0] if item['Instance']=='NONE' else item['Instance']
							del vals['Instance']
							for inst in instance_val:
								if 'Modifications' in item:
									mod_val = item['Modifications'][0]
									if mod_val['Frequency']=='':
										mod_val['Frequency']=['Total']
									vals['Modifications'] = mod_val
								new_json[f'{key}[{inst}]'] = vals
						else:
							if 'Modifications' in item:
								mod_val = item['Modifications'][0]
								if mod_val['Frequency']=='':
									mod_val['Frequency']=['Total']
									vals['Modifications'] = mod_val
							new_json[f'{key}[0]'] = vals
					continue






				if isinstance(value, list) and '[' not in key: #adding instance in brackets for all other keys
					for item in value:
						if 'Instance' in item:
							vals = item
							instance = 0 if item['Instance'] == 'NONE' else item['Instance']
							instance = [int(i) for i in instance] if isinstance(instance, list) else [instance]
							del vals['Instance']
							for inst in instance:
								new_json[f'{key}[{inst}]'] = vals
						else:
							new_json[f'{key}[0]'] = item
					continue




			final_json = {request: new_json} #changed format so the json is {request_num: info}

			output_path = os.path.join(new_folder, "try"+entry.name)
			with open(output_path, 'w') as f:
				json.dump(final_json, f, indent=4)


import json
import os, sys
import re
import traceback
from pymongo import MongoClient 






myclient = MongoClient("mongodb://localhost:27017/") 
db = myclient["Antibodies"]
Collection = db["json_files"]


def fusion(key, value):
	fusion_vals = value.split()
	new_key = 'Fusion'
	new_val = [int(fus) for fus in fusion_vals]
	return new_key, new_val

def note(old_key, key, value):
	base = old_key if '[' not in old_key else old_key.split('[')[0]
	if '[' in key:
		name_key, instance = key.split("[")
		instances = instance[:-1].strip().split(",")
		if len(instances)>1:
			new_key = f'{base}_Note'
			withinstance = [int(i) for i in instances[1:]]
			note_val = {'Note': value.strip(), 'Instance': int(instances[0]), 'WithInstances': withinstance}
			return new_key, note_val
		else:
			new_key = f'{base}_Note'
			note_val = {'Note': value.strip(), 'Instance': int(instances[0])}
			return new_key, note_val
	else:
		new_key = key
		note_val = {'Note': value.strip(), 'Instance': 0}
		return new_key, note_val

def antigen(key, value):
	if '[' in key:
		name_key, instance = key.split("[")
		instances = instance[:-1].strip().split(",")
	else:
		name_key = key
		instances = [0]
	gene = value.split(" ")[-1][1:-1].strip()
	antigen_raw_key = value.split(",")
	antigen = antigen_raw_key[0]
	antigen_raw_key.remove(antigen)
	if len(antigen_raw_key)>1:
		final_val = antigen_raw_key[-1].split('(')
		final_val = final_val[0].strip()
		antigen_raw_key.remove(antigen_raw_key[-1])
		antigen_raw_key.append(final_val)

		psuedonyms = [item.strip() for item in antigen_raw_key if item != gene]

		if len(instances)>1:
			antigen_key = name_key
			if 'a' not in instances[0]:
				antigen_val = {'Name':antigen.strip(), 'Instance': int(instances[0]), 'Gene': gene, 'Genesearch': re.sub(r'\d+', '', gene), 'Pseudonyms': psuedonyms, 'WithInstances': [int (i) for i in instances[1:]]}
			else: 
				antigen_val = {'Name':antigen.strip(), 'Instance': instances[0], 'Gene': gene, 'Genesearch': re.sub(r'\d+', '', gene), 'Pseudonyms': psuedonyms, 'WithInstances': [instances[1:]]}
			return antigen_key, antigen_val
		else:
			antigen_key = name_key
			antigen_val = {'Name':antigen.strip(), 'Instance': instances[0], 'Gene': gene, 'Genesearch': re.sub(r'\d+', '', gene), 'Pseudonyms': psuedonyms}
			return antigen_key, antigen_val
	else:
		if len(instances)>1:
			antigen_key = name_key
			antigen_val = {'Name':antigen.strip(), 'Instance': int(instances[0]), 'Gene': gene, 'Genesearch': re.sub(r'\d+', '', gene), 'WithInstances': [int (i) for i in instances[1:]]}
		else:
			antigen_key = name_key
			antigen_val = {'Name':antigen.strip(), 'Instance': int(instances[0]), 'Gene': gene, 'Genesearch': re.sub(r'\d+', '', gene)}

		return antigen_key, antigen_val

def chainlength(key, value):
	value = ''.join(filter(str.isalnum, value))
	if '[' in key:
		name_key, instance = key.split("[")
		instances = instance[:-1].strip().split(",")
		if len(instances)>1:
			chainlength_key = name_key
			chainlength_val = {'Instance': int(instances[0]), 'Value': int(value.strip()), 'WithInstances': [int(i) for i in instances[1:]]}
		else:
			chainlength_key = name_key
			chainlength_val = {'Instance': int(instances[0]), 'Value': int(value.strip())}
	else:
		chainlength_key = key
		chainlength_val = {'Instance': [0], 'Value': int(value.strip())}
	return chainlength_key, chainlength_val

def mutation(key, value):
	if '[' in key:
		mutations_key, instances = key.split("[")
		instances = instances[:-1].strip().split(",")
	else:
		mutations_key = key
		instances = [0]
	if '(' in value:
		mutations = value.split("(", 1)[0].strip().split(" ")
		reason = value.split("(", 1)[1][:-1]
		mutations_val = {'Mutations': mutations, 'Instances': [int(i) for i in instances], 'Reason': reason}
	else:
		mutations = value.strip()
		mutations_val = {'Mutations': mutations, 'Instances': [int(i) for i in instances]}
	return mutations_key, mutations_val

def info_range(key, value):
	value = value.strip()
	if '[' in key:
		range_key, instances = key.split("[")
		instances = instances[:-1].strip().split(",")
	else:
		range_key = key
		instances = [0]	
	if "(" in value:
		if "-" not in value:
			mutations = value[1:-1].split(" ")
			start = 0
			end = 0
		else:
			hinge_range, position = value.strip().split(" ", 1)  # split only once and test all scripts again
			mutations = [p for p in position[1:-1].split(" ")]
			start, end = [int(r) for r in hinge_range.split("-")]
	else:
		mutations = ['NONE']
		if '-' not in value:
			start = 0
			end = 0
		else:
			values = value.split('-')
			clean_vals = []
			for val in values:
				val = ''.join(filter(str.isalnum, val))
				clean_vals.append(val)
			start, end = [int(r) for r in clean_vals]


	range_val = {'Start': start, 'End': end, 'Mutations': mutations}

	return range_key, range_val


def cdrkabat(key, value):
	if '[' in key:
		cdr_key, instance = key.split('[')
		instances =  instance[:-1].strip().split(",")
	else:
		cdr_key = key 
		instances = [0]
	values = value.split()
	values = [val.strip() for val in values]
	sequence = values[0]
	start, end = list(map(int, value.strip().split(" ")[1][1:-1].split("-")))
	cdr_val = {'Sequence': sequence, 'Instances': [int(i) for i in instances], 'Start': start, 'End': end}
	return cdr_key, cdr_val

def germline(key, value):
	gene = value.split()[-1]
	species = value.split()[:len(value.split())-1]
	joined_species = " ".join(species)
	if joined_species not in germline_species_list:
		germline_species_list.append(joined_species)
		germline_dic[joined_species] = file_name
	if '[' in key:
		new_key, instance = key.split('[')
		instances =  instance[:-1].strip().split(",")
	else:
		new_key = key 
		instances = [0]	
	new_val = {'Species': joined_species, 'GeneID': gene, 'Instances': [int(i) for i in instances]}
	return new_key, new_val

def confirmed_ptm(key, value):
	if '[' in key:
		ptm_key, instance = key.split('[')
		instances =  instance[:-1].strip().split(",")
	else:
		ptm_key = key 
		instances = [0]		
	frequency = value.strip().split(" ")[-1][1:-1] if "(" in value else ["Total"]
	m_type = value.strip().split(" ")[0]
	position = [int(num) for num in value.strip().split(" ") if num.isnumeric()]
	ptm_val = {'Type': m_type, 'Instances': instances, 'Positions': position, 'Frequency': frequency}
	return ptm_key, ptm_val


def disulfides(key, value):
	if '[' in key:
		name_key, instance = key.split("[")
		if 'A' not in instance and 'B' not in instance:
			instance = list(map(int, (key.split("[", 1)[1][:-1].split(","))))
		if len(instance)>1:
			partner_inst = instance[1]
			dis_key = name_key
		else:
			partner_inst = instance[0]
			dis_key = name_key
	else:
		dis_key = key
		instance = 0
		partner_inst = [0]

	if 'DisulfidesIntra' in key:
		chain = 'L' if 'Light' in key else 'H'
		partner_chain = chain
	elif 'DisulfidesInter' in key:
		chain = 'H' if ('H' in key and 'L' not in key) else 'L'
		partner_chain = 'L' if ('L' in key and 'H' not in key) else 'H'
	else:
		bonds = value.split()
		for bond_pair in bonds:
			pair = bond_pair.split('-')
			dis_val = {'Instance': instance, 'Residue': int(pair[0]), 'PartnerResidue': int(pair[1]), 'PartnerInstances': partner_inst}
			return dis_key, dis_val


	disulfides_dic = []
	if value.strip()=='NONE':
		disulfides_dic.append({'ThisChain': chain, 'Instance': instance, 'Residue': 0, 'PartnerChain': partner_chain, 'PartnerResidue': 0, 'PartnerInstances': partner_inst})
		return dis_key, disulfides_dic

	bonds = value.split()
	for bond_pair in bonds:
		pair = bond_pair.split('-')

		disulfides_dic.append({'ThisChain': chain, 'Instance': instance, 'Residue': int(pair[0]), 'PartnerChain': partner_chain, 'PartnerResidue': int(pair[1]), 'PartnerInstances': partner_inst})

	return dis_key, disulfides_dic
 



folder_path = "/Users/emmawrenn/Downloads/inn-annotations-Consultation80"
directory = 'json_files'
new_folder = 'cleaned_json_files'
os.makedirs(new_folder, exist_ok=True)
cdr_sources = []
germline_species_list = []
germline_dic = {}
requests = []
for entry in os.scandir(folder_path): 
	if entry.is_file():
		file_name = os.path.basename(entry)

		if file_name=='00RNtoName.txt':
			with open(entry.path, "r", encoding="utf-8") as f:
				name_json = []
				for line in f:
					line = line.strip()
					if not line:
						continue
					parts = re.split(r"\s+", line)
					if parts[0].isnumeric():
						request = parts[0]
					else:
						request = parts[0]
					nums = parts[-2:]
					two_nums = True
					for num in nums:
						for val in num:
							if val.isnumeric()==False:
								two_nums = False

					if two_nums == True:
						PLNum = nums[0]
						CLNum = nums[1]
						name = " ".join(parts[1:-2])
						name_json.append({'Request': request, 'Name': name, 'PLNum': PLNum, 'CLNum': CLNum})
					else:
						if parts[-1].isnumeric():
							PLNum = parts[-1]
							name = " ".join(parts[1:-1])
							name_json.append({'Request': request, 'Name': name, 'PLNum': PLNum})
						else:
							ConsultationNum = parts[-1]
							name = " ".join(parts[1:-1])
						name_json.append({'Request': request, 'Name': name, 'ConsultationNum': ConsultationNum})

				request_to_name = {
					item["Request"]: item["Name"]
					for item in name_json
					if "Request" in item and "Name" in item
				}


for entry in os.scandir(folder_path): 
	if entry.is_file():
		try:
			new_json = {}
			file_name = os.path.basename(entry)
			if file_name=='00RNtoName.txt':
				continue

			with open(entry, 'r', encoding='utf-8') as f:

				content = [record.replace("\n", "") for record in f.read().split(";")]
				records = []
				for r in content:
					if "//" in r:
						chains = r.split('//')
						[records.append(c) for c in chains]
					else:
						records.append(r)
					records = [r.strip() for r in records if len(r) > 2]

				if "Format:" in records[0]:
					split_first_record = records[0].split("F", 1)
					split_first_record[1] = "F" + split_first_record[1]
					records = records[1:]
					for i in range(len(split_first_record) -1, -1, -1):
						records.insert(0, split_first_record[i])

				record_counter = 0 #keep this so it knows if the note is format or antigen

				for record in records:

					
					key, value = record.split(":", 1)
					if 'Request' in key:
						request = value.strip().split()[0]
						new_json['Request'] = request
						if request in request_to_name:
							new_json['Antibody_name'] = request_to_name[request]
						requests.append(request)
						if request == "12786":
							print("CURRENT WORKING DIRECTORY:", os.getcwd())
							print("SCRIPT FILE:", os.path.abspath(__file__))
							print("REQUEST:", repr(request))
							print("OUTPUT PATH:", os.path.abspath(output_path))

					elif 'Format' in key:
						new_json[key] = value.strip()
						count = record_counter
						while('Note' in record[count+1].split(':',1)[0]):
							new_key, note_val = note(record[count+1].split(':',1)[0], key, value)
							new_json[new_key] = note_val
							count+=1


					elif 'Fusion' in key and 'Protein' not in key:
						fusion_key, fusion_val = fusion(key, value)
						new_json[fusion_key] = fusion_val
					elif 'Note' in key:
						if 'Note' in records[record_counter-1]:
							i = 2
							while 'Note' in records[record_counter-i]:
								i+=1
							old_record = records[record_counter-i]
						else:
							old_record = records[record_counter-1] if 'Note' not in records[record_counter-1] else records[record_counter-2]

						old_key, old_val = old_record.split(":", 1)
						note_key, note_val = note(old_key, key, value)
						new_json[note_key] = note_val
					elif 'Domain' in key:
						if '[' in key:
							domain_key, instance = key.split('[')
							instances = instance[:-1].strip().split(",")
						else:
							domain_key = key
							instances = [0]
						if domain_key in new_json:
							existing_domain_dic = new_json[domain_key]
							existing_domain_dic['Instances'] = [existing_domain_dic['Instances'], [int(i) for i in instances]]
							existing_domain_dic['Values'] = [existing_domain_dic['Values'], value.split()]
							new_json[domain_key] = existing_domain_dic

						else:
							new_json[domain_key.strip()] = {'Values': value.split(), 'Instances': [int(i) for i in instances]}
					elif 'Antigen' in key:
						antigen_key, antigen_value = antigen(key, value)
						new_json[antigen_key] = antigen_value		
						count = record_counter
					elif 'CDRSource' in key:
						if '[' not in key:
							source_key = key.strip()
							instances = [0]
							source_val = {'Value': value.strip()}
						else: 
							source_key, instance = key.split("[")
							instances = instance[:-1].strip().split(",")
							if len(instance)>1:
								source_val = {'Value': value.strip(), 'Instances': [int(i) for i in instances]}
							else:
								source_val = {'Value': value.strip(), 'Instances': [int(i) for i in instances]}
								source_key = source_key.strip()
						if value.strip() not in cdr_sources:
							cdr_sources.append(value.strip())

						new_json[source_key] = source_val
					elif 'ChainLength' in key:
						chainlength_key, chainlength_val = chainlength(key, value)
						new_json[chainlength_key] = chainlength_val
					elif 'Mutation' in key:
						mutations_key, mutations_val = mutation(key, value)
						new_json[mutations_key] = mutations_val
					elif 'Range' in key:
						range_key, range_val = info_range(key, value)
						new_json[range_key] = range_val
					elif 'CDR' in key:
						cdr_key, cdr_val = cdrkabat(key, value)
						new_json[cdr_key.strip()] = cdr_val
					elif 'Germline' in key:
						germline_key, germline_val = germline(key, value)
						new_json[germline_key] = germline_val
					elif 'ConfirmedPTM' in key:
						ptm_key, ptm_val = confirmed_ptm(key, value)
						new_json[ptm_key] = ptm_val
					elif 'Disulfides' in key:
						dis_key, dis_val = disulfides(key, value)
						new_json[dis_key] = dis_val
					elif ' Chain' in key or 'Chain[' in key:
						if '[' in key:
							name_key, instance = key.split("[")
							if '-' in instance: #some values have '1-2-3' in the instance
								instances = instance[:-1].strip().split("-")
							else:
								instances = instance[:-1].strip().split(",")
						else:
							name_key = key
							instances = [0]
						new_json[name_key] = {'Sequence': value, 'Instances': [int(i) for i in instances]}
					elif 'ChainClass' in key:
						if '[' in key:
							class_key, instance = key.split("[")
							instances = instance[:-1].strip().split(",")
						else:
							class_key = key
							instances = [0]
						new_json[class_key] = {'Value': value.strip(), 'Instances': [int(i) for i in instances]}

					elif 'Potential' in key or 'ConfirmedN' in key:
						if '[' in key:
							name_key, instance = key.split("[")
							instances = instance[:-1].strip().split(",")
							seq = ['NONE'] if value.strip()=='NONE' else [int(val) for val in value.split()]
							new_json[name_key] = {'Positions': seq, 'Instances': [int(i) for i in instances]}
						else:
							seq = ['NONE'] if value.strip()=='NONE' else [int(val) for val in value.split()]
							new_json[key] = {'Sequence': seq, 'Instances': [0]}
					elif 'Linker' in key:
						if '[' in key:
							name_key, instance = key.split("[")
							instances = instance[:-1].strip().split(",")

							linker_key = name_key
							linker_val = {'Residues': value, 'Instances': [int(i) for i in instances]}
						else:
							linker_key = key
							linker_val = {'Residues': value, 'Instances': [0]}
						new_json[linker_key] = linker_val
					elif 'Type' in key:
						if '[' in key:
							name_key, instance = key.split("[")
							instances = instance[:-1].strip().split(",")
							instances = [int(i)for i in instances]
							if len(instances)>1:
								new_json[name_key] = {'Values': [value.strip()], 'Instances': [int(i) for i in instances]}
							else:
								new_json[name_key] = {'Values': [value.strip()], 'Instances': [int(i) for i in instances]}
						else:
							new_json[key] = {'Values': [value.strip()], 'Instances': [0]}
					elif 'Positions' in key:
						if value.strip() =='NONE':
							positions == [0]
						else:
							positions = value.split()
						if '[' in key:
							name_key, instance = key.split('[')
							instances = instance[:-1].strip().split(",")
							for instance in instances:
								new_json[name_key] = {'Values': [int(val) for val in positions], 'Instances': [int(i) for i in instances]}
						else:
							new_json[key] = {'Values': [int(val) for val in positions], 'Instances': [0]}

					else:
						new_json[key] = value







					record_counter+=1

				output_path = os.path.join(new_folder, request + ".json")
				with open(output_path, 'w') as f:
					json.dump(new_json, f, indent=4)
				if isinstance(new_json, list):
					Collection.insert_many(new_json)
				else:
					Collection.replace_one({"Request": request}, new_json, upsert=True)




		except Exception as e:
			print(f'error in file: {file_name}')
			print(f'error in record: {record}')
			traceback.print_exc()
			continue

result = Collection.delete_many({
	'Request': {
	'$regex': r'\.txt',
	'$options': 'i'
	}
})

white_space_deletes = Collection.delete_many({
	'Request': {
	'$regex': r'\ '
	}
})

wrong_files = Collection.delete_many({
	'Request': {
	'$exists': False
	}
})

print(f'deleted {result.deleted_count} documents')
print(f'deleted {white_space_deletes.deleted_count} documents')
print(f'deleted {wrong_files.deleted_count} documents')




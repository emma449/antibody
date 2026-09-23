from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
import re

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb://localhost:27017/")
db = client["Antibodies"]
collection = db["json_files"]

def normalise_list(values):
	return[v.strip() for v in values if v]


def build_query(filters):
	query = {}
	if filters.get('cdrSource'):
		cleaned = normalise_list(filters['cdrSource'])
		query['CDRSource.Value'] = {'$in': cleaned}

	if filters.get('heavyChainClass'):
		cleaned = normalise_list(filters['heavyChainClass'])
		query['HeavyChainClass.Value'] = {'$in': cleaned}
		print(cleaned)
	if filters.get('lightChainClass'):
		cleaned = normalise_list(filters['lightChainClass'])
		query['LightChainClass.Value'] = {'$in': cleaned}


	if filters.get('antibodySource'):
		cleaned_source = normalise_list(filters['antibodySource'])

		for source in cleaned_source:
			query.setdefault('$and', []).append(
				{'Format': {
					'$regex': r'\b' + source + r'\b',
					'$options': 'i'
				}
			})


	if filters.get('antibodyType'):
		cleaned_type = normalise_list(filters['antibodyType'])
		for type in cleaned_type:
			query.setdefault('$and', []).append(
				{'Format': {
					'$regex': r'\b' + type + r'\b',
					'$options': 'i'
				}
			})

	if filters.get('specialChain'):
		cleaned_chain = normalise_list(filters['specialChain'])
		chain_query = "(" + "|".join(cleaned_chain) + ")"
		query['Format'] = {
			'$regex': chain_query,
			'$options': 'i'
		}




	if filters.get('heavyPTMDic'):
		ptmdic = filters.get('heavyPTMDic')
		print(f'ptmdic:{ptmdic}')
		if ptmdic['potentialconfirmed'] == 'potential':
			query['HeavyPotentialPTM'] = {"$exists": True}
			if len(ptmdic['types'])>0:
				query['HeavyPotentialPTM.Type'] = {'$in': ptmdic['types']}
		elif ptmdic['potentialconfirmed'] == 'confirmed':
			query['HeavyConfirmedPTM'] = {"$exists": True}
			if len(ptmdic['types'])>0:
				print(ptmdic['types'])
				query['HeavyConfirmedPTM.Type'] = {'$in': ptmdic['types']}
		elif ptmdic['potentialconfirmed'] == 'both':
			print(ptmdic)
			if len(ptmdic['types'])>0:
				print(ptmdic['types'])
				query['$or'] = [
				{'HeavyPotentialPTM.Type': {'$in': ptmdic['types']}},
				{'HeavyConfirmedPTM.Type': {'$in': ptmdic['types']}}
				]
			else:
				query['$or'] = [
					{'HeavyPotentialPTM': {'$exists': True}},
					{'HeavyConfirmedPTM': {'$exists': True}}
				]


	if filters.get('lightPTMDic'):
		ptmdic = filters.get('lightPTMDic')
		if ptmdic['potentialconfirmed'] == 'potential':
			query['LightPotentialPTM'] = {"$exists": True}
			if len(ptmdic['types'])>0:
				query['LightPotentialPTM.Type'] = {'$in': ptmdic['types']}
		elif ptmdic['potentialconfirmed'] == 'confirmed':
			query['LightConfirmedPTM'] = {"$exists": True}
			if len(ptmdic['types'])>0:
				print(ptmdic['types'])
				query['LightConfirmedPTM.Type'] = {'$in': ptmdic['types']}
		elif ptmdic['potentialconfirmed'] == 'both':
			if len(ptmdic['types'])>0:
				query['$or'] = [
				{'LightPotentialPTM.Type': {'$in': ptmdic['types']}},
				{'LightConfirmedPTM.Type': {'$in': ptmdic['types']}}
				]
			else:
				query['$or'] = [
					{'LightPotentialPTM': {'$exists': True}},
					{'LightConfirmedPTM': {'$exists': True}}
				]


	if filters.get('heavyglycosDic'):
		glycosdic = filters.get('heavyglycosDic')
		print(f'glycos query: {glycosdic}')
		if glycosdic['potentialconfirmed'] == 'potential':
			if len(glycosdic['links'])>0:
				if 'n' in glycosdic['links']:
					query['HeavyPotentialNGlycos'] = {"$exists": True}
				if 'o' in glycosdic['links']:
					query['HeavyPotentialOGlycos'] = {"$exists": True}
			else:
				query['$or'] = [
					{'HeavyPotentialNGlycos': {'$exists': True}},
					{'HeavyPotentialOGlycos': {'$exists': True}}
				]
		elif glycosdic['potentialconfirmed'] == 'confirmed':
			if len(glycosdic['links'])>0:
				if 'n' in glycosdic['links']:
					query['HeavyConfirmedNGlycos'] = {"$exists": True}
				if 'o' in glycosdic['links']:
					query['HeavyConfirmedOGlycos'] = {"$exists": True}
			else:
				query['$or'] = [
					{'HeavyConfirmedNGlycos': {'$exists': True}},
					{'HeavyConfirmedOGlycos': {'$exists': True}}
				]
		elif glycosdic['potentialconfirmed'] == 'both':
			if len(glycosdic['links'])>0:
				if 'n' in glycosdic['links']:
					query['$or'] = [
						{'HeavyConfirmedNGlycos': {'$exists': True}},
						{'HeavyPotentialNGlycos': {'$exists': True}}
					]	
				if 'o' in glycosdic['links']:
					query['$or'] = [
						{'HeavyConfirmedOGlycos': {'$exists': True}},
						{'HeavyPotentialOGlycos': {'$exists': True}}
					]			
			else:
				query['$or'] = [
					{'HeavyConfirmedNGlycos': {'$exists': True}},
					{'HeavyConfirmedOGlycos': {'$exists': True}},
					{'HeavyPotentialOGlycos': {'$exists': True}},
					{'HeavyPotentialNGlycos': {'$exists': True}}
				]


	if filters.get('lightglycosDic'):
		glycosdic = filters.get('lightglycosDic')
		print(f'glycos query: {glycosdic}')
		if glycosdic['potentialconfirmed'] == 'potential':
			if len(glycosdic['links'])>0:
				if 'n' in glycosdic['links']:
					query['LightPotentialNGlycos'] = {"$exists": True}
				if 'o' in glycosdic['links']:
					query['LightPotentialOGlycos'] = {"$exists": True}
			else:
				query['$or'] = [
					{'LightPotentialNGlycos': {'$exists': True}},
					{'LightPotentialOGlycos': {'$exists': True}}
				]
		elif glycosdic['potentialconfirmed'] == 'confirmed':
			if len(glycosdic['links'])>0:
				if 'n' in glycosdic['links']:
					query['LightConfirmedNGlycos'] = {"$exists": True}
				if 'o' in glycosdic['links']:
					query['LightConfirmedOGlycos'] = {"$exists": True}
			else:
				query['$or'] = [
					{'LightConfirmedNGlycos': {'$exists': True}},
					{'LightConfirmedOGlycos': {'$exists': True}}
				]
		elif glycosdic['potentialconfirmed'] == 'both':
			if len(glycosdic['links'])>0:
				if 'n' in glycosdic['links']:
					query['$or'] = [
						{'LightConfirmedNGlycos': {'$exists': True}},
						{'LightPotentialNGlycos': {'$exists': True}}
					]	
				if 'o' in glycosdic['links']:
					query['$or'] = [
						{'LightConfirmedOGlycos': {'$exists': True}},
						{'LightPotentialOGlycos': {'$exists': True}}
					]			
			else:
				query['$or'] = [
					{'LightConfirmedNGlycos': {'$exists': True}},
					{'LightConfirmedOGlycos': {'$exists': True}},
					{'LightPotentialOGlycos': {'$exists': True}},
					{'LightPotentialNGlycos': {'$exists': True}}
				]			


	if filters.get('antigenDic'):
		antigenDic = filters.get('antigenDic')
		if len(antigenDic['names'])>0:
			cleaned_names = normalise_list(antigenDic['names'])
		if len(antigenDic['genes'])>0:
			cleaned_genes = normalise_list(antigenDic['genes'])
			gene_query = '|'.join(cleaned_genes)
			query['Antigen.Gene'] = {
				'$regex': gene_query,
				'$options': 'i'			
			}

		if len(antigenDic['species'])>0:
			cleaned_species = normalise_list(antigenDic['species'])
			species_query = '^(' + '|'.join(cleaned_species) + ')\\b' #species_query means the first word in Antigen.Name from the database can be queried, because this describes the species
			query['Antigen.Name'] = {
				'$regex': species_query,
				'$options': 'i'
			}

		if len(antigenDic['names'])>0:
			cleaned_names = normalise_list(antigenDic['names'])
			pattern = "(" + "|".join(antigenDic["names"]) + ")"
			query["Antigen.Name"] = {
				"$regex": pattern,
				"$options": "i"
			}

	if filters.get('antibody_name'):
		cleaned_names = normalise_list(filters.get('antibody_name'))
		name_query = '|'.join(cleaned_names)
		query['Antibody_name'] = {
				'$regex': name_query,
				'$options': 'i'
			}

	if filters.get('requests'):
		cleaned_nums = normalise_list(filters.get('requests'))
		request_query = '|'.join(cleaned_nums)
		query['Request'] = {
				'$regex': request_query,
				'$options': 'i'
			}



	if filters.get('germlineDic'):
		germline_map = {
			'hc': 'HCGermline',
			'hj': 'HJGermline',
			'hv': 'HVGermline',
			'lc': 'LCGermline',
			'lj': 'LJGermline',
			'lv': 'LVGermline'
		} #map germline type in germlinedic to the field in the json


		germlineDic = filters.get('germlineDic')
		for germline in germlineDic:
			g_type = germline.get('type')
			species = germline.get('species', [])
			genes = germline.get('genes', [])
			germline_type = germline_map.get(g_type)

			if not germline_type:
				continue

			query[germline_type] = {'$exists': True}

			if species:
				species_query = '|'.join(species)

				query[f'{germline_type}.Species'] = {
					'$regex': species_query,
					'$options': 'i'
				}

			if genes:
				cleaned_genes = normalise_list(genes)
				genes_query = '|'.join(re.escape(gene) for gene in cleaned_genes)
				print(genes_query)
				query[f'{germline_type}.GeneID'] = {
					'$regex': genes_query,
					'$options': 'i'
				}



	if filters.get('mutationDic'):
		mutationDic = filters.get('mutationDic')
		if mutationDic['present'] == False:
			query['MutationH'] = {"$exists": False}
			query['MutationL'] = {"$exists": False}
			query['Mutation'] = {"$exists": False}
		if mutationDic['present'] == True:
			mutation_criteria = [] #empty array to add conditions to
			if len(mutationDic['types'])>0:
				if 'mutationh' in mutationDic['types']:
					mutationHdic = {'MutationH': {"$exists": True}}
					if mutationDic['reasons']:
						mutationHdic['MutationH.Reason'] = {'$in': mutationDic['reasons']}
					mutation_criteria.append(mutationHdic)

				if 'mutationl' in mutationDic['types']:
					mutationLdic = {'MutationL': {"$exists": True}}
					if mutationDic['reasons']:
						mutationLdic['MutationL.Reason'] = {'$in': mutationDic['reasons']}
					mutation_criteria.append(mutationLdic)
				query['$or'] = mutation_criteria


			else:
				query['$or'] = [
					{'MutationH': {'$exists': True}},
					{'MutationL': {'$exists': True}},
					{'Mutation': {'$exists': True}}
				]
				if len(mutationDic['reasons'])>0:
						query['$or'] = [
							{'MutationH.Reason': {'$regex': '|'.join(mutationDic['reasons']), '$options': 'i'}},
							{'MutationL.Reason': {'$regex': '|'.join(mutationDic['reasons']), '$options': 'i'}},
							{'Mutation.Reason': {'$regex': '|'.join(mutationDic['reasons']), '$options': 'i'}}
						]







	return query


@app.route('/')
def home():
	return render_template('webtemplate.html')
	print('render')

@app.route("/search", methods = ['POST'])
def search():
	filters = request.json
	query = build_query(filters)
	print(f'query: {query}')

	results = list(collection.find(query, {"_id": 0}))


	return jsonify(results)


if __name__== '__main__':
	app.run(debug=True)
	print('ran')


#!/usr/bin/env python3
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
import re
import config

app = Flask(__name__)
CORS(app)

myclient = MongoClient("mongodb://" + config.mongodb_server + ":" + config.mongodb_port + "/") 
db = myclient["Antibodies"]
collection = db["json_files"]


#makes sure all values are cleaned of white spaces
def normalise_list(values):
	return[v.strip() for v in values if v]

#builds the search query from the filters
def build_query(filters):
	query = {}
	requests_names = [] #an array to build the queries for requests and antibody names, which are ORed with the rest of the query conditions

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
		sources = filters.get('antibodySource')
		cleaned_source = normalise_list(sources['values'])
		bool_key = '$or' if sources['bool'] == 'OR' else '$and'
		print(bool_key)

		for source in cleaned_source:
			query.setdefault(bool_key, []).append(
				{'Format': {
					'$regex': r'\b' + source + r'\b',
					'$options': 'i'
				}
			})


	if filters.get('antibodyType'):
		types = filters.get('antibodyType')
		print(types)
		cleaned_type = normalise_list(types['values'])
		bool_key = '$or' if types['bool'] == 'OR' else '$and'
		if len(types)>0:
			for type in cleaned_type:
				query.setdefault(bool_key, []).append(
					{'Format': {
						'$regex': r'\b' + type + r'\b',
						'$options': 'i'
					}
				})

	if filters.get('antibodySpecificity'):
		specs = filters.get('antibodySpecificity')
		cleaned_spec = normalise_list(specs['values'])
		bool_key = '$or' if specs['bool'] == 'OR' else '$and'
		for spec in cleaned_spec:
			if spec == 'monospecific':
				query.setdefault(bool_key, []).append(
					{'Format': {
						'$not': {
							'$regex': 'specific',
							'$options': 'i'
						}
					}
				})
			else:
				query.setdefault(bool_key, []).append(
					{'Format': {
						'$regex': spec,
						'$options': 'i'
					}
				})
		print(f'filters: {filters}')
		print(query)



	if filters.get('specialChain'):
		cleaned_chain = normalise_list(filters['specialChain'])
		for chain in cleaned_chain:
			query.setdefault('$and', []).append(
				{'Format': {
					'$regex': r'\b' + chain + r'\b',
					'$options': 'i'
				}
			})




	if filters.get('heavyPTMDic'):
		ptmdic = filters.get('heavyPTMDic')
		print(f'ptmdic:{ptmdic}')
		query['HeavyConfirmedPTM.Type'] = {'$all': ptmdic}


	if filters.get('lightPTMDic'):
		ptmdic = filters.get('lightPTMDic')
		query['LightConfirmedPTM.Type'] = {'$all': ptmdic}


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
		antigen_search = []

		if len(antigenDic['genes'])>0:
			cleaned_genes = normalise_list(antigenDic['genes'])
			gene_query = '|'.join(cleaned_genes) if antigenDic['bool'] == 'OR' else '&'.join(cleaned_genes)
			antigen_search.append({'Antigen.Gene': {
					'$regex': gene_query,
					'$options': 'i'	
				}		
			})

		if len(antigenDic['names'])>0:
			cleaned_names = normalise_list(antigenDic['names'])
			pattern = "(" + "|".join(antigenDic["names"]) + ")" if antigenDic['bool'] == 'OR' else "(" + "&".join(antigenDic["names"]) + ")"
			antigen_search.append({
				"Antigen.Name" : {
					"$regex": pattern,
					"$options": "i"
				}
			})

		if len(antigenDic['species'])>0:
			cleaned_species = normalise_list(antigenDic['species'])
			species_query = '^(' + '|'.join(cleaned_species) + ')\\b' #species_query means the first word in Antigen.Name from the database can be queried, because this describes the species
			query['Antigen.Name'] = {
				'$regex': species_query,
				'$options': 'i'
			}

		if len(antigen_search)>0:
			if antigenDic['bool'] == 'OR':
				query.setdefault('$and', []).append({
					'$or': antigen_search
				})
			else:
				query.setdefault('$and', []).extend(antigen_search)			



	if filters.get('antibody_name'):
		cleaned_names = normalise_list(filters.get('antibody_name'))
		name_query = '|'.join(cleaned_names)
		requests_names.append({
			'Antibody_name':{
				'$regex': name_query,
				'$options': 'i'
			}
		})


	if filters.get('requests'):
		cleaned_nums = normalise_list(filters.get('requests'))
		request_query = '|'.join(cleaned_nums)
		requests_names.append({
			'Request':{
				'$regex': request_query,
				'$options': 'i'
			}
		})



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
			germ_bool = germline['bool']

			germ_search = []

			if not germline_type:
				continue

			query[germline_type] = {'$exists': True}

			if species:
				species_query = '|'.join(species)

				germ_search.append({
					f'{germline_type}.Species' : {
					'$regex': species_query,
					'$options': 'i'
					}
				})

			if genes:
				cleaned_genes = normalise_list(genes)
				genes_query = '|'.join(re.escape(gene) for gene in cleaned_genes)
				print(genes_query)
				germ_search.append({
					f'{germline_type}.GeneID' : {
					'$regex': genes_query,
					'$options': 'i'
					}
				})

			if len(germ_search)==0:
				continue

			if germ_bool == 'OR':
				query.setdefault('$and', []).append({
					'$or': germ_search
				})
			else:
				query.setdefault('$and', []).extend(germ_search)



	mutationHDic = filters.get('mutationHDic')
	mutationLDic = filters.get('mutationLDic')

	if mutationHDic['present'] == False:
		query['MutationH'] = {"$exists": False}

	if mutationHDic['present'] is True:
		mutationDic = filters.get('mutationHDic')
		query['MutationH'] = {"$exists": True}
		#results will exclude any value with a mutation

		#create array of the reasons selected in the search query
		reasons = mutationDic.get('reasons', [])

		#check if MutationH is selected for (no selected types assumes any mutation present is selected for)
		if len(reasons)>0:
			query['MutationH.Reason'] = {'$all': reasons}

	if mutationLDic['present'] == False:
		query['MutationL'] = {"$exists": False}

	if mutationLDic['present'] is True:
		mutationDic = filters.get('mutationLDic')
		query['MutationL'] = {"$exists": True}

		#create array of the reasons selected in the search query
		reasons = mutationDic.get('reasons')

		#check if MutationH is selected for (no selected types assumes any mutation present is selected for)
		if len(reasons)>0:
			query['MutationL.Reason'] = {'$all': reasons}


	if requests_names:
		if len(query)>0:
			other_query = query.copy()


			query = {
				'$or': [*requests_names, other_query]
			}
		else:
			query = {'$or': requests_names}


	print(f'query with request {query}')


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


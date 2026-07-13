import pymongo 
from pymongo import MongoClient 
import sys 
import re 
import json

def add_to_query(query_parts, key, value, yesno): 
	query = '' 
	if yesno == "yes": 
		query = "{\"%s\" : {\"$regex\" : \".*%s.*\"}}" % (key, value) 
	elif yesno == "no": 
		query = "{\"%s\" : {\"$not\": {\"$regex\" : \".*%s.*\"}}}" % (key, value) 
	if query != "": 
 		query_parts.append(query)
	print(f'query parts: {query_parts}')
	return query_parts

# Combines the individual query parts into one query 
def combine_query_parts(query_parts): 
	query = ''
	if len(query_parts)==0:
		return ''
	elif len(query_parts) == 1:
		return query_parts[0]
	line_num = 0
	query = "{ \"$and\" : [\n" 
	for line in query_parts:
		query += " " + line
		line_num+=1
		if line_num < (len(query_parts)):
			query += ",\n"
		else:
			query += "\n"
	query += "]}" 
	return query

#old code just here in case something goes wrong. focus on new code below.





def add_regex_query(query_parts, key, value, yesno):
	if yesno=='yes':
		query_parts.append({
			key: {
				"$regex": value,
				"$options": "i"
			}
		})
	else:
		query_parts.append({
			key: {
				"$not": {
					"$regex": value,
					"$options": "i"
				}
			}
		})
	return query_parts


def add_exists_query(query_parts, key, yesno):
	if yesno=='yes':
		query_parts.append({
			key: {"$exists": True}
		})
	else:
		query_parts.append({
			key: {"$exists": False}
		})
	return query_parts


def combine_query(query_parts):
	if not query_parts:
		return {}

	if len(query_parts) == 1:
		return query_parts[0]

	return {"$and": query_parts}

# Runs the query. Converts the JSON query into a dictionary and runs it against the MongoDB database. 

def run_query(collection, query):
	if query == '':
		results = collection.find()
	else:
		results = collection.find(query)

	return results

if __name__ == "__main__":
	myclient = MongoClient("mongodb://localhost:27017/") 
	db = myclient["Antibodies"]
	collection = db["json_files"]
	query_parts = []  # Require the Format record contains 'bispecific' 
	query_parts = add_exists_query(query_parts, "MutationH", 'yes')
	query_parts = add_regex_query(query_parts, "Format", 'fusion', 'yes')
	query = combine_query(query_parts) 
	print(query)
	results = run_query(collection, query)
	print(results.next())
	count = collection.count_documents(query)
	print('count', count)
	print("all docs:", collection.count_documents({})) 
	print("trispecific:", collection.count_documents({
		"Format": {"$regex": ".*trispecific.*"}
	}))# Once we have a 'collection' variable (for our connection with the 
 # MongoDB database) we can call run_query() against the database 
 # results = run_query(collection, query)



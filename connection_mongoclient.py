import pymongo
from pymongo import MongoClient
import urllib.parse

username = urllib.parse.quote_plus('myUserAdmin')
password = urllib.parse.quote_plus('DE2G16project2022')
client = MongoClient("mongodb://%s:%s@192.168.2.234:38747" % (username, password))

# access the database
db = client['repo_jsons']

# access the collection in the database
# collection can be thought of as roughly the equivalent of a table in a relational database
collection = db['repos_2021']

print("successful connection")
#client.close()

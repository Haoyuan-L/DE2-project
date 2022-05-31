import pymongo
from pymongo import MongoClient
import pulsar
from web_crawler import runWebCrawler
import json

pulsar_client = pulsar.Client('pulsar://130.238.28.164:6650')
consumer = pulsar_client.subscribe('request', subscription_name='analysis-node') 

producer_one = pulsar_client.create_producer('response_one')
producer_two = pulsar_client.create_producer('response_two')
producer_three = pulsar_client.create_producer('response_three')
producer_four = pulsar_client.create_producer('response_four')

client = MongoClient("mongodb://192.168.2.234:27017")

col = client["repo_jsons"].get_collection("repos_2021")
#print(col.estimated_document_count())
"""
idx = 0
new_objects = []
for x in col.find():
    current_id = x["_id"]
    x["_id"] = idx
    idx += 1
    new_objects.append(x)
    col.delete_one({"_id": current_id})
col.insert_many(new_objects)
"""
while True:
    msg = consumer.receive()
    try:
        index = msg.data().decode("utf-8").split(" ")
        consumer.acknowledge(msg)
        print(index)
        start_index = int(index[0])
        end_index = int(index[2])
        test_counter = 0
        devop_counter = 0
        total = end_index - start_index + 1

        language_counter = {}
        top_repos = []

        while start_index <= end_index:
            repo = col.find_one({"_id": start_index})
            url = repo["repo"]["url"]
            test, devop = runWebCrawler(url)
            if test:
                test_counter += 1
            if test and devop:
                devop_counter += 1
            start_index += 1
            #print(repo["repo"]["commitsCount"])
            if repo["repo"]["primaryLanguage"] is None:
                language = "None"
            else: 
                language = repo["repo"]["primaryLanguage"]["name"]
            if language not in language_counter.keys():
                language_counter[language] = 1
            else:
                language_counter[language] += 1
            commits = 0
            if repo["repo"]["commitsCount"] is not None:
                commits = int(repo["repo"]["commitsCount"]["history"]["totalCount"])
            if len(top_repos) < 30:
                top_repos.append((url, commits))
            else:
                if top_repos[0][1] < commits:
                    top_repos[0] = (url,commits)
            top_repos = sorted(top_repos, key=lambda tup: tup[1])
        
        producer_one.send(json.dumps(language_counter).encode('utf-8'))
        producer_two.send(json.dumps(top_repos).encode('utf-8'))
        producer_three.send(f"{str(test_counter)} / {str(total)}".encode('utf-8'))
        producer_four.send(f"{str(devop_counter)} / {str(total)}".encode('utf-8'))
        #print(top_repos)
        #print(language_counter)
        #print(f"Test cases {str(test_counter)} / {str(total)}")
        #print(f"Devop & Test cases {str(devop_counter)} / {str(total)}")
    
    except:
        print("error")
        consumer.negative_acknowledge(msg)
#col.find().forEach(lambda doc: doc._id=):
#print(client.list_database_names())
client.close()

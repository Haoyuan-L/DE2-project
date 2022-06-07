import pymongo
from pymongo import MongoClient
import pulsar
from web_crawler import runWebCrawler
import json
import urllib.parse

pulsar_client = pulsar.Client('pulsar://130.238.28.164:6650')
consumer = pulsar_client.subscribe('request', subscription_name='analysis-node-1') 

producer_one = pulsar_client.create_producer('response_one')
producer_two = pulsar_client.create_producer('response_two')
producer_three = pulsar_client.create_producer('response_three')
producer_four = pulsar_client.create_producer('response_four')

username = urllib.parse.quote_plus('myUserAdmin')
password = urllib.parse.quote_plus('DE2G16project2022')
client = MongoClient("mongodb://%s:%s@192.168.2.234:38747" % (username, password))

col = client["all_repos_2"].get_collection("All_2021Repos")
print(col.estimated_document_count())


while True:
    msg = consumer.receive()
    
    try:
        index = msg.data().decode("utf-8").split(" ")
        consumer.acknowledge(msg)
        print(index)
        start_index = int(index[0])
        end_index = int(index[2])
        total = end_index - start_index + 1
        language = "None"
        language_counter = {}
        test_language_counter = {}
        devop_language_counter = {}
        top_repos = []

        while start_index <= end_index:
            repo = col.find_one({"id": str(start_index)})
            if repo is None:
                start_index += 1
                continue
            url = repo["repo"]["url"]
            test, devop = runWebCrawler(url)
            print(start_index)
            if start_index % 25 == 0:
                print(start_index)
            
            if repo["repo"]["primaryLanguage"] is not None:
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
            top_repos = sorted(top_repos, key=lambda tup: tup[1], reverse=True)
       
            if test:
                if language not in test_language_counter.keys():
                    test_language_counter[language] = 1
                else:
                    test_language_counter[language] += 1
            if test and devop:
                if language not in devop_language_counter.keys():
                    devop_language_counter[language] = 1
                else:
                    devop_language_counter[language] += 1
            start_index += 1
        
        producer_one.send(json.dumps(language_counter).encode('utf-8'))
        producer_two.send(json.dumps(top_repos).encode('utf-8'))
        producer_three.send(json.dumps(test_language_counter).encode('utf-8'))
        producer_four.send(json.dumps(devop_language_counter).encode('utf-8'))
        #print(top_repos)
        #print(language_counter)
        #print(f"Test cases {str(test_counter)} / {str(total)}")
        #print(f"Devop & Test cases {str(devop_counter)} / {str(total)}")
    
    except Exception as e:
        print(str(e))
        consumer.negative_acknowledge(msg)
#col.find().forEach(lambda doc: doc._id=):
#print(client.list_database_names())

client.close()

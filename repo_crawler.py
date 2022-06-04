import requests
import json
import datetime
import time
import pymongo
from pymongo import MongoClient
import urllib
import urllib.request
from urllib.error import HTTPError
import urllib.parse

header = {"Authorization": "token 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"}
username = urllib.parse.quote_plus('myUserAdmin')
password = urllib.parse.quote_plus('DE2G16project2022')

# A simple function to create database for this script
def get_database():
    client = MongoClient("mongodb://%s:%s@192.168.2.234:38747" % (username, password))
    return client["all_repos_2"]

def run_query(query, variables, headers):
    request = requests.post("https://api.github.com/graphql", json={'query': query, 'variables': variables}, headers=header)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}".format(request.status_code))


def make_query(after_cursor):
    return """
      query ($query: String!) {
        search(
          type: REPOSITORY,
          query: $query,
          first: 100,
          after: AFTER
        ) {
          pageInfo {
            hasNextPage
            endCursor
          }
          repos: edges {
            repo: node {
              ... on Repository {
                url
                name
                allIssues: issues {
                  totalCount
                }
                openIssues: issues(states:OPEN) {
                  totalCount
                }
                primaryLanguage {
                  name
                }
                commitsCount: object(expression: "master") {
                  ... on Commit {
                    history {
                      totalCount
                    }
                  }
                }
              }
            }
          }
        }
        rateLimit {
            limit
            cost
            remaining
            resetAt
        }
      }
    """.replace(
        "AFTER", '"{}"'.format(after_cursor) if after_cursor else "null"
    )


if __name__ == '__main__':
    start_time = time.time()
    has_next_page = True
    after_cursor = None
    start_date = datetime.date(2021, 1, 1)
    end_date = datetime.date(2021, 12, 31)
    delta = datetime.timedelta(days=1)
    dbname = get_database()
    collection_name = dbname["All_2021Repos"]
    file = open('365_days_pages_jsons.txt', 'w')

    # search limit sloved, narrow down the search range
    print("start to fetch data!\n")
    index = 1

    while start_date <= end_date:
        print("Start to fetch {} repos data.\n".format(start_date))
        variables = {
            "query": "created:" + str(start_date)
        }
        # pagination solved by traverse the next cursor
        while has_next_page:
            while True:
                try:
                    data = run_query(query=make_query(after_cursor), variables=variables, headers=header)
                    break
                except (HTTPError, requests.exceptions.HTTPError, requests.exceptions.RequestException, Exception) as err:
                    print("{}. Retry in 300 seconds!\n".format(err))
                    time.sleep(300)
                    continue
            for repo in data["data"]["search"]["repos"]:
                repo["id"] = str(index)
                index += 1
                json.dump(repo, file, indent=4)
                collection_name.insert_one(repo)
            has_next_page = data["data"]["search"]["pageInfo"]["hasNextPage"]
            after_cursor = data["data"]["search"]["pageInfo"]["endCursor"]
        rate_limit = int(data["data"]["rateLimit"]["remaining"])
        print("The remaining limit points is {}\n".format(rate_limit))
        if rate_limit <= 10:
            print("Token requests reach the limit, starting sleep!")
            time.sleep(3600)
            print("Token request limitation has resumed!")
        has_next_page = True
        start_date += delta

    execution_time = time.time() - start_time
    print("The fetching job is done!\n")
    print("The elapsed time is {} seconds!\n".format(execution_time))
    file.close()



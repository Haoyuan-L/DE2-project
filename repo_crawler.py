from python_graphql_client import GraphqlClient
import requests
import json
import datetime

client = GraphqlClient(endpoint="https://api.github.com/graphql")
header = {"Authorization": "token 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"}

# A simple function to use requests.post to make the API call. Note the json= section.
def run_query(query, variables):
    request = requests.post("https://api.github.com/graphql", json={'query': query, 'variables': variables},
                            headers=header)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


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
    repos = []
    has_next_page = True
    after_cursor = None
    start_date = datetime.date(2021, 1, 1)
    end_date = datetime.date(2021, 1, 3)
    delta = datetime.timedelta(days=1)

    # search limit sloved, narrow down the search range
    while start_date <= end_date:
        variables = {
            "query": "created:" + str(start_date)
        }
        # pagination solved by traverse the next cursor
        while has_next_page:
            data = client.execute(query=make_query(after_cursor), variables=variables, headers=header)
            print(json.dumps(data, indent=4))
            print()
            for repo in data["data"]["search"]["repos"]:
                repos.append(repo)
            has_next_page = data["data"]["search"]["pageInfo"]["hasNextPage"]
            after_cursor = data["data"]["search"]["pageInfo"]["endCursor"]
        has_next_page = True
        start_date += delta

    file = open('3_days_pages_jsons.txt', 'w')
    file.write(json.dumps(repos, indent=4))
    file.close()



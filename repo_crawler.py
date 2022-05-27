from python_graphql_client import GraphqlClient
import requests
import json

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
    variables = {
        "query": "created:2021-01-01",
    }

    while has_next_page:
        data = client.execute(query=make_query(after_cursor), variables=variables, headers=header)
        print(json.dumps(data, indent=4))
        print()
        for repo in data["data"]["search"]["repos"]:
            repos.append(repo)
        has_next_page = data["data"]["search"]["pageInfo"]["hasNextPage"]
        after_cursor = data["data"]["search"]["pageInfo"]["endCursor"]

    file = open('10pages_jsons.txt', 'w')
    file.write(json.dumps(repos, indent=4))
    file.close()



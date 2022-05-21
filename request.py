import requests
import pandas as pd

url = "https://api.github.com/search/repositories?q=-pushed:<2021-01-01-created:>2021-12-31&per_page=100&page=10"

header = {
  "Accept": "application/vnd.github.v3+json",
  "Authorization": "token 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"
}

res = requests.get(url, headers=header)
repos = res.json()
jsons = pd.read_json(repos)

while 'next' in res.links.keys():
  res = requests.get(res.links['next']['url'], headers=header)
  repos.update(res.json())
print(repos["items"])





#Restful Api, deprecated
import requests
import pandas as pd
import datetime

start_date = datetime.date(2021, 1, 1)
end_date = datetime.date(2021, 1, 3)
delta = datetime.timedelta(days=1)

header = {
  "Accept": "application/vnd.github.v3+json",
  "Authorization": "token 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"
}

while start_date <= end_date:
    url = "https://api.github.com/search/repositories?q=created:" + str(start_date) + "&per_page=100&page=1"
    res = requests.get(url, headers=header)
    repos = res.json()
    json = pd.DataFrame.from_dict(repos)
    if str(start_date) == "2021-01-01":
        jsons = json
    else:
        jsons = pd.concat([jsons, json], ignore_index=True)
    while 'next' in res.links.keys():
        res = requests.get(res.links['next']['url'], headers=header)
        repos = res.json()
        json = pd.DataFrame.from_dict(repos)
        jsons = pd.concat([jsons, json], ignore_index=True)
    start_date += delta
    print(jsons)



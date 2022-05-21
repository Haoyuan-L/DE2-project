from github import Github


access_token = "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"
g = Github(access_token, per_page=10000)
repos = g.search_repositories(query="created:2021-01-01..2021-12-31 or pushed:2021-01-01..2021-12-31")
print(repos.get_page(1))



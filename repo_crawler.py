from github import Github

access_token = "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"

g = Github(access_token)
print(g.get_user().get_repos())

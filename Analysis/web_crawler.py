import requests
import json
from bs4 import BeautifulSoup
import re

test_keywords = ["test", "build.sh"]
ci_cd_keywords = ["ci", "cd", "travis.yml", "gitlab-ci.yml", "drone.yml", ".github"]

if __name__ == '__main__':

    with open("github_json.txt") as f:
        data = json.load(f)
    for entry in data["data"]["search"]["repos"]:
        test = False
        ci = False
        url = entry["repo"]["url"]
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        print(url)
        for el in soup.find_all("a", class_="js-navigation-open Link--primary"):
            name = el.getText()
            if not test:
                for keyword in test_keywords:
                    regexp = re.compile(keyword)
                    if regexp.search(name):
                        print("test exists")
                        test = True
                        break
            if not ci:
                for keyword in ci_cd_keywords:
                    regexp = re.compile(keyword)
                    if regexp.search(name):
                        print("ci exists")
                        ci = True
                        break







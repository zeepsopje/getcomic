#!/usr/bin/env python3
import os
import sys
import requests
import shutil
from simple_term_menu import TerminalMenu
from bs4 import BeautifulSoup

base_url = 'https://readcomicsonline.ru'

def result_slugs(obj):
    return obj['data']

def result_names(obj):
    return obj['value']

# Gets the user's query
def get_query():
    if len(sys.argv) == 1:
        return input("Type a keyword of the comic you want to download: ")
    else:
        return sys.argv[1]

# Performs a search
def search(q):
    r = requests.get(f"{base_url}/search?query={q}")
    return r.json()['suggestions']

def menu(options):
    menu = TerminalMenu(options)
    return menu.show()

def main():
    q = get_query()
    results = search(q)

    if len(results) == 0:
        print(f"No results found for '{q}'")
        sys.exit()

    comic = menu(map(result_names, results))
    comic_name = results[comic]['data']
    comic_path = f"./{comic_name}"

    try:
        os.mkdir(comic_path)
    except FileExistsError:
        pass

    # Request comic page and get all issues
    r = requests.get(f"{base_url}/comic/{results[comic]['data']}")
    soup = BeautifulSoup(r.text, features='html5lib')
    issues = soup.select('ul.chapters > li')

    # Transform issues soup into dictionary
    for i, issue in enumerate(issues):
        url = issue.h5.a['href']
        value = {
            'url': url,
            'num': i+1,
            'slug': url.split('/')[5],
            'value': issue.h5.get_text().strip()
        }
        issues[i] = value

    issue = issues[menu(map(result_names, issues))]
    issue_path = f"{comic_path}/{issue['slug']}"

    try:
        os.mkdir(issue_path)
    except FileExistsError:
        pass

    count = 1
    while True:
        filename = "%02d.jpg" % (count)
        url_compound = issue['url'].split('/')
        img_loc = '/'.join([
            url_compound[0],
            url_compound[1],
            url_compound[2],
            'uploads/manga',
            url_compound[4],
            'chapters',
            url_compound[5],
            "%02d.jpg" % (count)
        ])

        r = requests.get(img_loc, stream = True)

        if r.status_code != 200:
            break

        print('Downloading page %d...' % count)

        r.raw.decode_content = True

        with open(f"{issue_path}/{filename}", 'wb') as f:
            shutil.copyfileobj(r.raw, f)

        count += 1

if __name__ == '__main__':
    main()

import numpy as np
import pandas as pd

import requests
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from lxml import etree, html
from io import StringIO

from fake_useragent import UserAgent
import random

from multiprocessing import Pool

import time


def get_proxies():
    global proxies

    url = 'https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=1500&country=all&ssl=all&anonymity=elite&uptime=80'
    response = requests.get(url)
    new_proxies = response.text.split()
    
    print("First 10 proxies:")
    for p in new_proxies[:10]:
        print(" - {}".format(p))
    
    proxies = set(new_proxies)

    if len(proxies):
        print("Got my proxy list! {} proxies".format(len(proxies)))
        
    else:
        print("Failed to get proxies!")
        exit()

def retrieve_url(url):
    global proxies

    if len(proxies) < 100:
        get_proxies()

    # Don't slam the arxiv too hard
    sleep = np.random.rand() * 10.
    print("Waiting {:.2f}s to obfuscate crawling".format(sleep))
    time.sleep(sleep)
    proxy = proxies.pop()

    print("Querying {} with the proxy {}".format(url, proxy))
    # print("Querying {} with no proxy".format(url))

    try:
        response = requests.get(url, proxies={'https': proxy, 'http': proxy})
        print("The request return code {}".format(response.status_code))
        # If the proxy worked, put it back in the list of proxies.
        proxies.add(proxy)
    except:
        print("Failed to retrieve {} with the proxy: {}\n".format(url, proxy))
        response = retrieve_url(url)

    return response

def scrape_authors(YYMM):
    '''Takes a year, month and arxiv index, and grabs the author list from it.
    Returns a list of the authors, and the arxiv code of the paper. If the code is invalid,
    None is returned instead of a list of authors
    
    Arguments:
    ----------
    YYMM: str
    
    Returns:
    --------
    data: dict
        A dict of the form {arxiv ID: [author list]}
    '''

    # Templates to crawl over
    urlTemplate = "https://arxiv.org/abs/{}"
    codeTemplate = "{:4s}.{:05d}"

    print("Getting the year and month: {}".format(YYMM))

    data = {}

    N = 0
    while True:
        N += 100
        # Construct the URL
        code = codeTemplate.format(YYMM, N)
        url = urlTemplate.format(code)

        # Get the page
        page = retrieve_url(url)

        print("Got the page from the url")

        soup = BeautifulSoup(page.content, 'lxml')

        # Find the div that contains the list of authors
        authorBox = soup.find('div', {'class': 'authors'})

        if authorBox is None:
            print("Finished {}".format(YYMM))
            break
        else:
            # Extract the author names from that list.
            authorNames = authorBox.find_all('a')
            authorNames = [author.getText() for author in authorNames]

            data[code] = authorNames
            print("Got {} authors from {}".format(len(authorNames), url))

    return data


if __name__ in "__main__":
    ## Bits and bobs to stop my getting blocked by the site's robo-racist
    ua = UserAgent() # From here we generate a random user agent
    proxies = [] # Will contain proxies [ip, port]


    # Retrieve latest proxies
    print("Getting proxies")
    get_proxies()


    # Test the new implimentation
    YYMM = '1001'
    records = scrape_authors(YYMM)

    from pprint import pprint
    pprint(records)


    codes = []
    for Y in range(9, 20):
        for M in range(1, 13):
            codes.append("{:02d}{:02d}".format(Y, M))
    p = Pool(100)
    records = p.map(scrape_authors, codes)

    # Graceful process shutdown
    p.terminate()
    p.join()

    with open('ArXiv_Scrape.txt', 'w') as f:
        for entry in records:
            for key in entry.keys():
                authors = ["'{}'".format(a) for a in entry[key]]
                authors = ", ".join(authors)

                line = "{}, {}\n".format(key, authors)
                f.write(line)


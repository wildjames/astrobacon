import numpy as np
import pandas as pd

import requests
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import feedparser
from lxml import etree, html
from io import StringIO

from fake_useragent import UserAgent
import random

from multiprocessing import Pool

import time


def get_proxies():
    global proxies

    with open('proxyURL.txt', 'r') as f:
        url = f.read().strip()
    response = requests.get(url)
    new_proxies = response.text.split()
    
    print("First 10 proxies:")
    for p in new_proxies[:10]:
        print(" - {}".format(p))
    
    proxies = new_proxies

    if len(proxies):
        print("Got my proxy list! {} proxies".format(len(proxies)))
        
    else:
        print("Failed to get proxies!")
        exit()
    
    with open("proxies.tmp", 'w') as f:
        f.write(response.text)

def retrieve_url(url, use_proxy=True):
    
    # Don't slam the arxiv too hard
    sleep = np.random.rand() * 10.
    time.sleep(sleep)

    if use_proxy:
        with open("proxies.tmp", 'r') as f:
            proxies = f.read().split()

        headers = {'User-Agent':str(ua.chrome)}
        proxy = random.choice(proxies)

        print("Querying {} with the proxy {}".format(url, proxy))
    else:
        print("Querying {} with no proxy".format(url))

    try:
        if use_proxy:
            response = requests.get(url, 
                proxies={'https': proxy, 'http': proxy}, 
                headers=headers,
                timeout=30)
            if response.status_code == 503:
                print("The proxy {} is banned :(".format(proxy))
                raise Exception
            if response.status_code == 504: # server error
                raise Exception
        else:
            response = requests.get(url, timeout=30)
        print("The url {} request returned: code {}".format(url, response.status_code))
    except:
        print("Failed to retrieve {} with the proxy: {}".format(url, proxy))
        proxies.remove(proxy)
        with open("proxies.tmp", 'w') as f:
            for p in proxies:
                if p != proxy:
                    f.write("{}\n".format(p))
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
    urlTemplate = "http://export.arxiv.org/api/query?id_list={}"
    codeTemplate = "{:4s}.{:05d}"

    print("Getting the year and month: {}".format(YYMM))

    data = {}

    Ns = np.arange(15000)
    random.shuffle(Ns)
    for N in Ns:
        # Construct the URL
        code = codeTemplate.format(YYMM, N)
        url = urlTemplate.format(code)

        # Get the page
        page = retrieve_url(url, True)

        ## Check that the page returned a paper
        content = feedparser.parse(page.text)
        try:
            entries = content.entries[0]
        except:
            print("!!FAILED!! The ArXiv ID http://arxiv.org/abs/{}".format(code))
            continue
        
        authors = entries['authors']
        authorNames = [a['name'] for a in authors]
        # print(authorNames)
        
        if len(authorNames) > 1:
            data[code] = authorNames
            print("\nSuccessfully got the author list from http://arxiv.org/abs/{}\n".format(code))
        elif len(authorNames) == 1:
            print("\nOnly 1 author for paper http://arxiv.org/abs/{}\n".format(code))

    return data


if __name__ in "__main__":
    ## Bits and bobs to stop my getting blocked by the site's robo-racist
    ua = UserAgent() # From here we generate a random user agent
    proxies = [] # Will contain proxies [ip, port]


    # Retrieve latest proxies
    print("Getting proxies")
    get_proxies()


    codes = []
    for Y in range(17, 19):
        for M in range(1, 13):
            codes.append("{:02d}{:02d}".format(Y, M))


    # Call the arxiv API and get the author lists of each ID in each month.
    p = Pool(40)
    records = p.map(scrape_authors, codes)
    # Graceful finish
    p.terminate()
    p.join()


    with open('ArXiv_Scrape.txt', 'w') as f:
        for entry in records:
            for key in entry.keys():
                authors = ["'{}'".format(a) for a in entry[key]]
                authors = ", ".join(authors)

                line = "{}, {}\n".format(key, authors)
                f.write(line)


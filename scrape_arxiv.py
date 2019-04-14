import numpy as np
import pandas as pd
import requests

from bs4 import BeautifulSoup

from lxml import etree
from io import StringIO


def scrape_authors(Y, M, N):
    '''Takes a year, month and arxiv index, and grabs the author list from it.
    Returns a list of the authors, and the arxiv code of the paper. If the code is invalid,
    None is returned instead of a list of authors
    
    Arguments:
    ----------
    Y: int
        The year of publication
    
    M: int
        The month of publication
    
    N: int
        The index of publication
        
    Returns:
    --------
    authorNames: list(str)
        A list of the authors on this paper
    
    code: str
        The arxiv code of this paper
    '''

    Y = int(Y)
    M = int(M)
    N = int(N)

    # Templates to crawl over
    urlTemplate = "https://arxiv.org/abs/{}"
    codeTemplate = "{:02d}{:02d}.{:05d}"

    # Construct the URL
    code = codeTemplate.format(Y, M, N)
    url = urlTemplate.format(code)
    # print("Grabbing authors from {}".format(url))

    # Get the page
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'lxml')

    # Find the div that contains the list of authors
    authorBox = soup.find('div', {'class': 'authors'})

    if authorBox is None:
        print("Failed to get the authorbox")
        return code, None
    else:
        # Extract the author names from that list.
        authorNames = authorBox.find_all('a')
        authorNames = [author.getText() for author in authorNames]

        return code, authorNames



# data = pd.DataFrame(columns=['Name', 'Publications'])
authorPapers = {}
paperAuthors = {}

# Example paper
YY = 18
MM = 1
N  = 1
    
N = 10600


while True:
    N += 1

    # look at the page
    code, authors = scrape_authors(YY, MM, N)

    if authors is None:
        break

    print("Paper: https://arxiv.org/abs/{}, {} authors".format(code, len(authors)))

    # I only care when a paper has more than one author
    if len(authors) < 2:
        continue

    # Store the authors I do care about
    for a in authors:
        try:
            authorPapers[a].append(code)
        except:
            authorPapers[a] = [code]
    # Also store the reverse for use later.
    paperAuthors[code] = authors

for key in authorPapers.keys():
    print("{:>20s}: {}".format(key, authorPapers[key]))
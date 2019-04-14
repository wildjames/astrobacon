import numpy as np
import requests

from bs4 import BeautifulSoup

from lxml import etree
from io import StringIO


def scrape_authors(Y, M, N):
    '''Takes a year, month and arxiv index, and grabs the author list from it.
    Returns a list of the authors, and the arxiv code of the paper. If the code is invalid,
    an empty list is returned.
    
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
    print("Grabbing authors from {}".format(url))

    # Get the page
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'lxml')

    # Find the div that contains the list of authors
    authorBox = soup.find('div', {'class': 'authors'})

    if authorBox is None:
        return code, []
    else:
        # Extract the author names from that list.
        authorNames = authorBox.find_all('a')
        authorNames = [author.getText() for author in authorNames]

        return code, authorNames




# Example paper
YY = 7
MM = 1
N  = 45


c, a = scrape_authors(YY, MM, N)
print(a)
import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


if __name__ in "__main__":
    # The scraped data from ArXiv
    dfname = 'ArXiv_Scrape.txt'

    # Store the connections as dicts of authors for now
    authorPapers = {}
    paperAuthors = {}
    authorList = set()

    # There are some edge cases that are easier to just to handle like this
    reject = ['', '"', "'", 'USA']

    with open(dfname, 'r') as f:
        for line in f:
            line = line.strip().split(',')
            paper = line[0]
            authors = [x.strip() for x in line[1:] if x.strip() not in reject]
            
            paperAuthors[paper] = list(authors)
            for author in authors:
                authorList.add(author)
                try:
                    authorPapers[author].append(paper)
                except:
                    authorPapers[author] = [paper]
    authorList = list(authorList)

    # Init the graph
    G=nx.MultiGraph()

    # Add the authors to it to it
    for author in authorList:
        G.add_node(author)

    # Add the connections
    for author in authorPapers.keys():
        for paper in authorPapers[author]:
            for coauthor in paperAuthors[paper]:
                G.add_edge(author, coauthor)
    

    # Find a path between two random authors
    cont = True
    i = 0
    while cont:
        i += 1
        a1 = random.choice(authorList)
        a2 = random.choice(authorList)
        try:
            path = nx.dijkstra_path(G, a1, a2)
            print("The two authors, {} and {}, are linked by the following chain:".format(a1, a2))
            print(path)
            cont = False
        except:
            print("No path between {} and {}".format(a1, a2))
            cont = True

    print(" I had to search {} author pairs, of {} authors before finding a link.".format(i, len(authorList)))
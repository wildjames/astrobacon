import random
import itertools
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

from pprint import pprint

if __name__ in "__main__":
    # The scraped data from ArXiv
    dfname = 'ArXiv_OAI.txt'

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
    


    a1 = 'S. J. Edberg'
    a2 = 'S. Miyazaki'

    while True:
        a1 = random.choice(authorList)
        a2 = str(a1)
        while a1 == a2:
            a2 = random.choice(authorList)


        # Test cases
        # a1 = 'K. Torii'
        # a2 = 'I. A. Nekrasov'

        # a1 = 'Barry Y. Welsh'
        # a2 = 'Timothy M. Heckman'

        try:
            path = nx.dijkstra_path(G, a1, a2)
        except:
            print("No path between {} and {}".format(a1, a2))
            continue


        # This graph will only draw the two linked authors
        H = nx.MultiGraph()

        print("\n\nThe two authors, {} and {}, are linked by the following chain:".format(a1, a2))
        print(path)
        print("They're separated by {} degrees.".format(len(path)))


        # Add the linking path between the authors
        H.add_nodes_from(path)
        
        # I need to jump through some hoops to label these, it looks complex but the logic is fine.
        paper_trail = []
        toLabel = {}

        # Look at every paper we have
        for paper in paperAuthors.keys():
            # Make a set, as these will be faster to process
            authors = set(paperAuthors[paper])
            
            # intersection returns common elements between the two
            crossover = authors.intersection(set(path))
            if len(crossover) ==  2:
                # print("{} has the crossover {}".format(paper, crossover))
                
                # Add the paper to our paper trail
                paper_trail.append(paper)
                for a, b in itertools.combinations(crossover, 2):
                    toLabel[tuple([a, b])] = paper
                    
                    if not b in H.nodes():
                        H.add_node(b)
                    if not a in H.nodes():
                        H.add_node(a)
                    
                    H.add_edge(a, b)


        # Fill in the other (semi-irrelevant) coauthor nodes, to get an idea of which papers are 'hub' papers
        for author in path:
            for paper in authorPapers[author]:
                for coauthor in paperAuthors[paper]:
                    if not coauthor in H.nodes():
                        H.add_node(coauthor)
                    
                        H.add_edge(author, coauthor)
        
        Nnodes = H.number_of_nodes()
        Nconns = H.number_of_edges()

        print("The graph has {} Authors on it, and {} links between them!".format(Nnodes, Nconns))

        pos = nx.spring_layout(H)
        nodes = H.node()
        node_size = [100 if n in path else 3 for n in nodes]
        node_weights = [10 if n in path else 1 for n in nodes]

        nx.draw_networkx_labels(H, pos=pos, font_size=8, font_weight='bold', labels={i:i for i in path})
        nx.draw_networkx_edge_labels(H, pos=pos, font_size=5, edge_labels=toLabel)
        nx.draw_networkx_nodes(H, pos=pos, node_size=node_size, node_color='red')
        nx.draw_networkx_edges(H, pos=pos, alpha=0.3)
        
        plt.tight_layout()
        plt.show()

        del H
import random
import itertools
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

from pprint import pprint

if __name__ in "__main__":
    # The scraped data from ArXiv
    dfname = 'ArXiv_Scrape.txt'

    # Store the connections as dicts of authors for now
    authorPapers = {}
    paperAuthors = {}
    authorList = set()

    # There are some edge cases that are easier to just to handle like this
    reject = ['', '"', "'", 'USA']

    print("Making a graph connecting the authors in {}".format(dfname))
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
    print("Made a graph linking {} authors".format(len(authorList)))

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

        # Try and find a path linking the two authors. If none is found, try another combination
        try:
            path = nx.dijkstra_path(G, a1, a2)
        except:
            print("No path between {} and {}".format(a1, a2))
            continue


        # This graph will only draw the two linked authors
        H = nx.MultiGraph()

        print("\n\nThe two authors, {} and {}, are linked by the following chain:".format(a1, a2))
        print(path)
        print("They're separated by {} degrees.".format(len(path)-1))


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

                # For each combintaion of the authors in the path that are on this paper
                for a, b in itertools.combinations(crossover, 2):
                    # Create a label for them
                    toLabel[tuple([a, b])] = paper
                    
                    # Add a node for that author, if it's not already added.
                    if not b in H.nodes():
                        H.add_node(b)
                    if not a in H.nodes():
                        H.add_node(a)
                    
                    # And join those nodes
                    H.add_edge(a, b)


        # Fill in the other (semi-irrelevant) coauthor nodes, to get an idea of which authors are 'hub' authors
        for author in path:
            for paper in authorPapers[author]:
                for coauthor in paperAuthors[paper]:
                    if not coauthor in H.nodes():
                        H.add_node(coauthor)
                        H.add_edge(author, coauthor)
        

        Nnodes = H.number_of_nodes()
        Nconns = H.number_of_edges()
        print("The graph has {} Authors on it, and {} links between them all".format(Nnodes, Nconns))

        # Pre-compute the draw locations, so I can customise the appearance
        pos = nx.spring_layout(H)

        # Set the sizes, so that authors on the path have larger nodes
        nodes = H.node()
        node_size = [100 if n in path else 3 for n in nodes]

        # Draw the graph!
        nx.draw_networkx_labels(H, pos=pos, font_size=8, font_weight='bold', labels={i:i for i in path})
        nx.draw_networkx_edge_labels(H, pos=pos, font_size=5, edge_labels=toLabel)
        nx.draw_networkx_nodes(H, pos=pos, node_size=node_size, node_color='red')
        nx.draw_networkx_edges(H, pos=pos, alpha=0.3)
        plt.gca().set_axis_off()

        plt.tight_layout()
        plt.show()

        del H
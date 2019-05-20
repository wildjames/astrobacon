import sickle
from pprint import pprint

db = sickle.Sickle("http://export.arxiv.org/oai2")

print("Getting the database...")
records = db.ListRecords(metadataPrefix='arXiv')
print("Done! Getting data...")

with open('ArXiv_OAI.txt', 'w') as f:
    for record in records:
        try:
            paper = record.metadata['id'][0]
        except:
            print("Couldn't get the paper ID!")
            # pprint(record.metadata)

            continue

        try:
            surnames = record.metadata['keyname']
        except:
            print("Couldn't get the paper keynames!")
            # pprint(record.metadata)

            continue

        try:
            forenames = record.metadata['forenames']
        except:
            print("Couldn't get the paper Forenames!")
            # pprint(record.metadata)
            forenames = ['' for _ in surnames]


        authors = []
        for firstName, lastName in zip(forenames, surnames):
            a = "{} {}".format(firstName, lastName)
            authors.append(a)

        authors = ', '.join(authors)
        line = "{}, {}\n".format(paper, authors)
        
        print(line, end='')
        f.write(line)
        
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

            forenames = record.metadata['forenames']
            surnames = record.metadata['keyname']
            authors = []
            for firstName, lastName in zip(forenames, surnames):
                a = "{} {}".format(firstName, lastName)
                authors.append(a)

            authors = ', '.join(authors)
            line = "{}, {}\n".format(paper, authors)
            f.write(line)
        except:
            paper = record.metadata['id']
            if type(paper) is list:
                paper = paper[0]
            else:
                print("Something weird!")
                pprint(record)
            a = ', '.join(record.metadata['keyname'])
            line = "{}, {}\n".format(paper, a)
            f.write(line)
        else:
            print("\n\n\n\nThe following paper was problematic - it probably has a collaboration or something similar.")
            pprint(record.metadata)
            print(record.metadata['id'])
            print(record.metadata['keyname'])
            print(record.metadata['forenames'])
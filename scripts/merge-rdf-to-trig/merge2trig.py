from rdflib import Graph, URIRef, Literal
from rdflib.namespace import SKOS, RDF, RDFS
import rdflib.term
import os, fnmatch
from datetime import datetime

def find(pattern, path, datasets = None): #datasets is only used for vocabulary data where we need to specify the ones whose alignment data we want to merge
    presult = []
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if datasets is None: # we are handling record data not vocabularies
                if fnmatch.fnmatch(name, pattern):
                    result.append(os.path.join(root, name))
            else:
                for dataset in datasets:
                    if fnmatch.fnmatch(name, pattern) and name.find(dataset) != -1:
                        presult.append(name)
                        break
        if len(presult) > 0 :
            presult.sort(reverse=True)
            name = presult[0]
            result.append(os.path.join(root, name))
            presult.clear()
    return result

def findlastchar(string, char):
    flag = -1
    for i in range(len(string)):
        if (string[i] == char):
            flag = i

    if (flag == -1):
        return None
    else:
        return (flag + 1)

#*
#* Process records
#*

# find each subdirectory except from "scripts"
# datasets = ['bod','loc','sul','tna']
#
# # find the rdf files for each dataset
# for dataset in datasets:
#     fgraphs = {}
#     files = find('*.rdf', '../../' + dataset, "records")
#     # for each file
#     for file in files:
#         lastslashpos = findlastchar(file, "/")
#         recname = file[lastslashpos:-4]
#         fgraphs[recname] = Graph()
#         try: # some validation is required for well-formness
#             fgraphs[recname].parse(file, format = "xml")
#         except:
#             print("File: " + file + " did not parse correctly.")
#
#     dgraph = Graph()
#
#     for fgraph in fgraphs.values():
#         dgraph = dgraph + fgraph
#
#     curdt = datetime.now()
#     dgraph.qname(URIRef("http://www.ligatus.org.uk/lcd/board-pilot/" + dataset + "-" + curdt.strftime("%Y-%m-%d"))) # this does not do anything, not sure how to set the URI on the named graph
#     dgraph.serialize("../../" + dataset + "/" + dataset + "-data-" + curdt.strftime("%Y-%m-%d") + ".trig", "trig")
#     print(dataset + " complete")

#*
#* Process vocabularies matches into a single trig file without SKOS Scheme statements (RS does not like multiple scheme statements)
#*

# find each subdirectory except from "scripts"
datasets = ['bod-vocab','loc-vocab','sul-vocab','tna-vocab']

# find the rdf files for each dataset
for dataset in datasets:
    fgraphs = {}

    files = find('*.ttl', '../../../conservation-vocabularies/align/', datasets)

    # for each file
    for file in files:
        lastslashpos = findlastchar(file, "/")
        recname = file[lastslashpos:-4]
        fgraphs[recname] = Graph()

        try: # some validation is required for well-formness
            fgraphs[recname].parse(file, format = "turtle")
        except:
            print("File: " + file + " did not parse correctly.")

        # remove any SKOS ConceptScheme statements
        subjects = fgraphs[recname].subjects(RDF.type, URIRef('http://www.w3.org/2004/02/skos/core#ConceptScheme'))
        for subject in subjects:
            fgraphs[recname].remove((subject, RDF.type, URIRef('http://www.w3.org/2004/02/skos/core#ConceptScheme')))
        # remove any SKOS inScheme statements
        subject_objects = fgraphs[recname].subject_objects(URIRef('http://www.w3.org/2004/02/skos/core#inScheme'))
        for subject_object in subject_objects:
            fgraphs[recname].remove((subject_object[0], URIRef('http://www.w3.org/2004/02/skos/core#inScheme'), subject_object[1]))
        # remove any SKOS topConceptOf statements
        subject_objects = fgraphs[recname].subject_objects(URIRef('http://www.w3.org/2004/02/skos/core#topConceptOf'))
        for subject_object in subject_objects:
            fgraphs[recname].remove((subject_object[0], URIRef('http://www.w3.org/2004/02/skos/core#topConceptOf'), subject_object[1]))
        # remove any SKOS hasTopConcept statements
        subject_objects = fgraphs[recname].subject_objects(URIRef('http://www.w3.org/2004/02/skos/core#hasTopConcept'))
        for subject_object in subject_objects:
            fgraphs[recname].remove((subject_object[0], URIRef('http://www.w3.org/2004/02/skos/core#hasTopConcept'), subject_object[1]))
        # remove any DC creator statements
        subject_objects = fgraphs[recname].subject_objects(URIRef('http://purl.org/dc/elements/1.1/creator'))
        for subject_object in subject_objects:
            fgraphs[recname].remove((subject_object[0], URIRef('http://purl.org/dc/elements/1.1/creator'), subject_object[1]))
        # remove any DCT right statements
        subject_objects = fgraphs[recname].subject_objects(URIRef('http://purl.org/dc/terms/rights'))
        for subject_object in subject_objects:
            fgraphs[recname].remove((subject_object[0], URIRef('http://purl.org/dc/terms/rights'), subject_object[1]))

    dgraph = Graph()

    for fgraph in fgraphs.values():
        dgraph = dgraph + fgraph

curdt = datetime.now()
dgraph.qname(URIRef("http://www.ligatus.org.uk/lcd/board-pilot/vocab-align-" + curdt.strftime("%Y-%m-%d"))) # this does not do anything, not sure how to set the URI on the named graph
dgraph.serialize("../../../conservation-vocabularies/align/vocab-align-data-" + curdt.strftime("%Y-%m-%d") + ".trig", "trig")
print("vocabulary alignment data merged")
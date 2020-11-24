from rdflib import Graph, URIRef, Literal
from rdflib.namespace import SKOS, RDF, RDFS
import rdflib.term
import os, fnmatch
from datetime import datetime

def find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
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

# find each subdirectory except from "scripts"
datasets = ['bod','loc','sul']

# find the rdf files for each dataset
for dataset in datasets:
    fgraphs = {}
    files = find('*.rdf', '../../' + dataset)
    # for each file
    for file in files:
        lastslashpos = findlastchar(file, "/")
        recname = file[lastslashpos:-4]
        fgraphs[recname] = Graph()
        try: # some validation is required for well-formness
            fgraphs[recname].parse(file)
        except:
            print("File: " + file + " did not parse correctly.")

    dgraph = Graph()

    for fgraph in fgraphs.values():
        dgraph = dgraph + fgraph

    curdt = datetime.now()
    dgraph.qname(URIRef("http://www.ligatus.org.uk/lcd/board-pilot/" + dataset + "-" + curdt.strftime("%Y-%m-%d"))) # this does not do anything, not sure how to set the URI on the named graph
    dgraph.serialize("../../" + dataset + "/" + dataset + "-data-" + curdt.strftime("%Y-%m-%d") + ".trig", "trig")
    print(dataset + " complete")
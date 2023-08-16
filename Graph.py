import networkx as nx
import csv
from collections import defaultdict
import time
from random import sample, choice, shuffle, randint
import itertools
from Concept import *

def load_concepts_to_graph(input_labels, graph):
    f = open(input_labels, "r")
    lines = f.readlines()
    for line in lines:
        line = line.rstrip("\n")
        tokens = line.split("\t")
#         if tokens[2]=='1':
#             status = 'defined'
#         else:
#             status = 'primitive'
        #con = Concept(tokens[0], tokens[1].lower(), status)
        #graph.add_node(tokens[0], label=tokens[1].lower(), data=con)
        con = Concept(tokens[0], tokens[1])
        graph.add_node(tokens[0], label=tokens[1], data=con)
    f.close()
    return graph


def load_isa_relations_to_graph(input_hierarchyFile, graph):
    f = open(input_hierarchyFile, "r")
    lines = f.readlines()
    for line in lines:
        line = line.rstrip("\n")
        tokens = line.split("\t")
        graph.add_edge(tokens[0], tokens[1])
        # if tokens[1] == 'is_a':
        #     graph.add_edge(tokens[0], tokens[2])
    f.close()
    return graph


def load_networkx_graph(input_labelsFile, input_hierarchyFile):
    graph = nx.DiGraph()
    load_concepts_to_graph(input_labelsFile, graph)
    load_isa_relations_to_graph(input_hierarchyFile, graph)
    print('Number of nodes: ', graph.number_of_nodes())
    print('Number of edges: ', graph.number_of_edges())
    return graph


def load_attribute_rels_to_graph(graph, attribute_rel_file):
    f = open(attribute_rel_file, "r")
    lines = f.readlines()
    for line in lines:
        line = line.rstrip("\n")
        tokens = line.split("\t")
        child_obj = graph.nodes[tokens[0]]['data']   # child Concept object
        #parent_obj = graph.nodes[tokens[2]]['data']  # parent Concept object
        parent_id = tokens[2]
        rel = tokens[1]

        #prnt_set = None
        if rel not in child_obj.attribute_rels:
            prnt_set = set()
        else:
            prnt_set = child_obj.attribute_rels[rel]

        prnt_set.add(parent_id)
        child_obj.attribute_rels[rel] = prnt_set

    f.close()
    return graph


def load_subconcepts_to_graph(graph, subconcepts_file):
    with open(subconcepts_file, 'r') as txtfile:
        lines = txtfile.readlines()
        for line in lines:
            line = line.rstrip("\n")
            tokens = line.split("\t")
            conid = tokens[0]
            subconcepts = tokens[1].split(',')
            con_obj = graph.nodes[conid]['data']
            con_obj.subconcepts = set(subconcepts)



def obtainSubhierarchy(graph, subhierarchyID):
    descendants = nx.ancestors(graph, subhierarchyID)
    descendants.add(subhierarchyID)
    #print(len(descendants))
    subgrph = graph.subgraph(descendants)
    print("Number of nodes in subhierarchy: ",subgrph.number_of_nodes())
    print("Number of edges in subhierarchy: ",subgrph.number_of_edges())
    return subgrph

# THIS ISN"T USEFUL. MULTIPLE CONCEPTS COULD HAVE THE SAME PF. THEIR FSNs WILL BE DIFFERENT WITH THE SEMANTIC TAG
def preferredName_to_id_map_0(labels_file):
    prefnm_id = {}  # key = preffered name (without semantic tag in FSN), value = SNOMED id
    f = open(labels_file, "r")
    lines = f.readlines()
    for line in lines:
        line = line.rstrip("\n")
        tokens = line.split("\t")
        id = tokens[0]
        partitions = tokens[1].rpartition(' (')
        prefnm_id[partitions[0].lower()] = id
    f.close()
    return prefnm_id

# returns a mapping between a preferred names and a set of SNOMED CT concept IDs with that preferred name
def preferredName_to_id_map(labels_file):
    prefnm_ids = defaultdict(set)  # key = preffered name (without semantic tag in FSN), value = SNOMED id
    f = open(labels_file, "r")
    lines = f.readlines()
    for line in lines:
        line = line.rstrip("\n")
        tokens = line.split("\t")
        id = tokens[0]
        pf_name = tokens[1].rpartition(' (')[0].lower()
        # if pf_name in prefnm_ids:
        #     id_set = prefnm_ids[pf_name]
        # else:
        #     id_set = set()
        # id_set.add(id)
        # prefnm_ids[pf_name] = id_set
        # print(line, ' **** ', pf_name)
        prefnm_ids[pf_name].add(id)
    f.close()
    return prefnm_ids

def write_subhierarchy_conceptIDLabels_to_file(subhierarchy_graph, output_file):
    with open(output_file, 'w') as output_file:
        for conID in subhierarchy_graph.nodes():
            output_file.write(conID + '\t' + subhierarchy_graph.nodes[conID]['data'].label + '\n')

    print('Subhierarchy concept id and label written to file!!')


def write_subhierarchy_isa_to_file(subhierarchy_graph, output_file):
    with open(output_file, 'w') as output_file:
        for conID in subhierarchy_graph.nodes():
            for parent in subhierarchy_graph.successors(conID):
                output_file.write(conID + '\t' + parent + '\n')

    print('Subhierarchy is-a relations written to file!!')

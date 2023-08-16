#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 21:22:53 2020

@author: rashmie
"""

import networkx as nx
#import csv
#import time
import itertools
from Graph import *
import graphviz

class NLS:
    def __init__(self, nls_string, hierarchyGraph):
        self.nls_string = nls_string
        tokens = nls_string.split(";")
        self.lower_bound = tokens[0].split('|')
        self.upper_bound = tokens[1].split('|')
        self.all_concept = tokens[2].split('|')
        self.edges = tokens[3].split(",")
        self.graph = hierarchyGraph.subgraph(self.all_concept)
        #self.graph_withConceptLabels = self.createGraph(conID_label_dict)
        self.size = int(tokens[4])

    # def createGraph_withConceptLabels(self, conID_label_dict):
    #     edge_list = []
    #     for edge in self.edges:
    #         pair = edge.split("|")
    #         edge_list.append((conID_label_dict[pair[0]], conID_label_dict[pair[1]]))
    #     g = nx.DiGraph()
    #     g.add_edges_from(edge_list)
    #     return g

    # formats the original label so that '/' ar eescaped and longer labels are put in multiple lines
    def formatLabel(self, original_label):
        max_characters_per_line = 15
        original_label.replace("\\", "\\\\")
        words = original_label.split(" ")
        # formatted_label_list = []
        formatted_label = ""
        line = ""
        for word in words:
            if len(line) == 0:
                line = word + " "
            elif (len(line) + len(word)) <= max_characters_per_line:
                line = line + " " + word + " "
                # print(word)
            else:
                line = line.strip()
                # if len(formatted_label)==0:
                #     formatted_label = line+"\\n"
                # else:
                #     formatted_label = formatted_label+""+line+"\\n"

                formatted_label = formatted_label + line + "\\n"
                line = word
        line = line.strip()
        formatted_label = formatted_label + line
        # formatted_label = formatted_label[:-3]
        return formatted_label

    def saveGraphToPNG(self, conID_label_dict, output_folder_path):
        g = graphviz.Digraph()
        g.graph_attr['rankdir'] = 'BT'
        # g.attr(fontsize='20')
        # g.graph_attr['fontsize'] = '1.0'
        # g.attr(fontsize='1')

        for conID in self.all_concept:
            g.node(conID, self.formatLabel(conID_label_dict[conID]))

        edge_list = []
        for edge in self.edges:
            pair = edge.split("|")
            edge_list.append((pair[0], pair[1]))
        g.edges(edge_list)

        with g.subgraph() as s:
            s.attr(rank='same')
            for con in self.lower_bound:
                s.node(con)

        with g.subgraph() as s:
            s.attr(rank='same')
            for con in self.upper_bound:
                s.node(con)

        g.format = 'png'
        g.render(output_folder_path+self.lower_bound[0]+'_'+self.lower_bound[1])
        
    def getNonRelationsInBounds(self):
        non_relations = set()
        for concept_pair in itertools.combinations(self.lower_bound, 2):
            non_relations.add((concept_pair[0], concept_pair[1]))
            non_relations.add((concept_pair[1], concept_pair[0]))
        for concept_pair in itertools.combinations(self.upper_bound, 2):
            non_relations.add((concept_pair[0], concept_pair[1]))
            non_relations.add((concept_pair[1], concept_pair[0]))
        return non_relations


    def getNonRelationsInLowerBound(self):
        non_relations = set()
        for concept_pair in itertools.combinations(self.lower_bound, 2):
            non_relations.add((concept_pair[0], concept_pair[1]))
            non_relations.add((concept_pair[1], concept_pair[0]))
        return non_relations

    # returns (A, B) if A is-a B or B is-a A does not exists in the ontology
    def getAllNonRelations(self):
        non_relations = set()
        for concept_pair in itertools.combinations(self.graph.nodes(), 2):
            if (not nx.has_path(self.graph, concept_pair[0], concept_pair[1])) and (not nx.has_path(self.graph, concept_pair[1], concept_pair[0])):
                non_relations.add((concept_pair[0], concept_pair[1]))
                non_relations.add((concept_pair[1], concept_pair[0]))
        return non_relations


    def isNonRelationExists(self, nonRel):
        child, parent = nonRel
        if (child in self.all_concept) and (parent in self.all_concept) and (not nx.has_path(self.graph, child, parent)):
            return True

        return False

    def isNonRelationExistsInBounds(self, nonRel):
        child, parent = nonRel
        if ((child in self.lower_bound and parent in self.lower_bound) or (child in self.upper_bound and parent in self.upper_bound)) and not nx.has_path(self.graph, child, parent):
            return True
        return False


def loadNLSsFromHierarchy(hierarchy_graph, NLS_input, nls_maxSize):
    nls_set = set()
    f = open(NLS_input, "r")
    lines = f.readlines()
    for line in lines:
        line = line.rstrip("\n")
        tokens = line.split(";")
        ub_cons = tokens[0].split('|')
        #print(ub_cons[0])
        if not hierarchy_graph.has_node(ub_cons[0]):     #upper bound concepts are the most general concepts in the NLS. If they are children of the subhierarchy root, the entire NLS is under the subhierarchy root.
            continue
        elif nls_maxSize is not None and int(tokens[4])>nls_maxSize:
            continue
        else:
            nls_set.add(NLS(line, hierarchy_graph))
    f.close()
    print('Num NLSs: ', len(nls_set))
    return nls_set


def write_NLS_nonRels_to_file(nls_set, output_file):
    nls_non_relations = set()
    for i, nls in enumerate(nls_set):
        print('NLS ', i, ' processing')
        for con1, con2 in nls.getAllNonRelations():
            nls_non_relations.add((con1, con2))

    print('Num NLS non-relations: ', len(nls_non_relations))

    with open(output_file, 'w') as output_file:
        for con1, con2 in nls_non_relations:
            output_file.write(con1 + '\t' + con2 + '\n')

    print('NLS non-relations written to file!!')


def write_NLS_LB_NonRels_to_file(nls_set, output_file):
    nls_non_relations = set()
    for i, nls in enumerate(nls_set):
        print('NLS ', i, ' processing')
        for con1, con2 in nls.getNonRelationsInLowerBound():
            nls_non_relations.add((con1, con2))

    print('Num NLS non-relations: ', len(nls_non_relations))

    with open(output_file, 'w') as output_file:
        for con1, con2 in nls_non_relations:
            output_file.write(con1 + '\t' + con2 + '\n')

    print('NLS non-relations written to file!!')


def load_NLS_nonRels_from_file(input_file):
    nls_nonRels = set()
    with open(input_file, 'r') as txtfile:
        lines = txtfile.readlines()
        for line in lines:
            line = line.rstrip("\n")
            tokens = line.split("\t")
            nls_nonRels.add((tokens[0], tokens[1]))

    print('Number of NLS non-rels loaded: ', len(nls_nonRels))
    return nls_nonRels


def write_nls_strings_to_file(nls_set, output_file):
    with open(output_file, 'w') as output_file:
        for nls in nls_set:
            output_file.write(nls.nls_string + '\n')

    print('Non-lattice subgraphs written to file!!')



def main():
    start_time = time.time()

    # G = load_networkx_graph("inputs/SNOMED/activeConcept_ID_FSN_20190901.txt", "inputs/SNOMED/activeISA_20190901.txt")
    #
    # subhierarchy_graph = obtainSubhierarchy(G, "404684003")
    # nlss = loadNLSsFromHierarchy(subhierarchy_graph, "inputs/SNOMED/SNOMEDCT_2019September_NLSs.txt", 6)
    # print('nlss: ', len(nlss))
    # nonRels_inBounds = set()
    # for nls in nlss:
    #     nonRels_inBounds.update(nls.getNonRelationsInBounds())
    # print("nonRels_inBounds: ", len(nonRels_inBounds))

    G = load_networkx_graph("inputs/SNOMED/snomed_20210301_labels_status.txt", "inputs/SNOMED/snomed_20210301_hierarchy.txt")
    #subhierarchy_graph = obtainSubhierarchy(G, "373873005")
    #nls_set = loadNLSsFromHierarchy(subhierarchy_graph, "inputs/SNOMED/snomed_20210301_nlss.txt", None)
    #write_NLS_nonRels_to_file(nls_set, 'inputs/SNOMED/snomed_20210301_nls_nonRels.txt')
    #load_NLS_nonRels_from_file('inputs/SNOMED/snomed_20210301_nls_nonRels.txt')

    #write_nls_strings_to_file(nls_set, 'inputs/SNOMED/snomed_20210301_root_373873005_nlss.txt')

    subhierarchy_root = '404684003' # clinical finding
    subhierarchy_graph = obtainSubhierarchy(G, subhierarchy_root)
    nls_set = loadNLSsFromHierarchy(subhierarchy_graph, "inputs/SNOMED/snomed_20210301_nlss.txt", 6)
    write_NLS_nonRels_to_file(nls_set, 'inputs/SNOMED/snomed_20210301_clinical_finding_small_nls_LB_nonRels.txt')







    print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == "__main__":
    main()
## Transitive closure considering the combination of different types of relations in GO

import networkx as nx
import csv
import copy
import time

graph = None
concept_dict = None #key = con id, value = Concept instance

class Concept:
    def __init__(self, id, label):
        self.id = id
        self.label = label  # fully specified name
        self.id_label = id+' '+label
        #self.status = status    # status = primitive/defined

        self.pref_name = self.label.rpartition(' (')[0]

        self.valid = None      # Concept labels not starting with 'product containing' or 'product containing only' are invalid

        #e.g. label = Product containing promazine in parenteral dose form (medicinal product form)
        self.pre = None     # e.g. Product containing
        self.ingredient = None     # promazine
        self.dose_form = None        # in parenteral dose form
        self.partition_pref_name()  # partitions the preferred name to pre, ingredient and dose_form and assigns the values to class attributes above

        self.attribute_rels = {}    # dict: key=relation, value=set of parents connected by the relation
        self.subconcepts = set()    # other ontology concepts existing as substring of the preferred name of this concept

        self.parents = {}   #dict: key=relation, value=parents
        self.ancestors = {} #dict: key=relation, value=ancestors
        # self.all_ancestors = set()  # all ancestors connected by any relation
        self.root = None

        #self.sequence_of_words = None
        #self.set_of_words = None
        #self.pos_tags = None # each element here corresponds to an element of sequence_of_words

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Concept):
            return self.id == other.id
        return False


    def partition_pref_name(self):
        if self.pref_name.startswith('product containing only'):
            self.valid = True
            self.pre = 'product containing only'

            if ' in ' in self.pref_name:    # contains dose_form
                partitions = self.pref_name.replace('product containing only ', '', 1).rpartition(' in ')
                self.ingredient = partitions[0]
                self.dose_form = partitions[2]
            else:   # does not contain does_form
                self.ingredient = self.pref_name.replace('product containing only ', '', 1)

        elif self.pref_name.startswith('product containing'):
            self.valid = True
            self.pre = 'product containing'

            if ' in ' in self.pref_name:  # contains dose_form
                partitions = self.pref_name.replace('product containing ', '', 1).rpartition(' in ')
                self.ingredient = partitions[0]
                self.dose_form = partitions[2]
            else:   # does not contain dose_form
                self.ingredient = self.pref_name.replace('product containing ', '', 1)
        else:
            self.valid = False


    def get_sequence_of_words(self):
        if self.sequence_of_words is None:
            self.sequence_of_words = self.label.strip().split(' ')
        return self.sequence_of_words

    def get_set_of_words(self):
        if self.set_of_words is None:
            self.set_of_words = set(self.get_sequence_of_words())
        return self.set_of_words

    def is_a_ancestors(self, graph):
        if 'is_a' in self.ancestors:
            return self.ancestors['is_a']

        self.ancestors['is_a'] = nx.descendants(graph, self.id)
        return self.ancestors['is_a']

    def is_a_ancestors_0(self):
        if 'is_a' in self.ancestors:
            return self.ancestors['is_a']

        isa_ancs = set()
        if 'is_a' in self.parents:
            isa_ancs.update(self.parents['is_a'])
            for isa_anc in self.parents['is_a']:
                isa_ancs.update(concept_dict[isa_anc].is_a_ancestors())

        self.ancestors['is_a'] = isa_ancs
        return self.ancestors['is_a']

    def part_of_ancestors(self):
        #isa_ancestors = self.is_a_ancestors()
        #isa_ancestors = nx.descendants(graph, self.id)
        if 'part_of' in self.ancestors:   #if ancestors has been previously computed
            return self.ancestors['part_of']

        partof_ancs = set()

        if 'is_a' in self.parents:
            for isa_anc in self.parents['is_a']:
                partof_ancs.update(concept_dict[isa_anc].part_of_ancestors())   # part-of ancestors of is-a ancestors

        if 'part_of' in self.parents:
            partof_ancs.update(self.parents['part_of'])  # part of parents
            for partof_anc in self.parents['part_of']:
                partof_ancs.update(concept_dict[partof_anc].part_of_ancestors())   #partof ancestors of partof parents
                partof_ancs.update(concept_dict[partof_anc].is_a_ancestors())  # isa ancestors of partof parents

        self.ancestors['part_of'] = partof_ancs
        return partof_ancs

    def find_all_ancs_closure(self):
        self.is_a_ancestors()
        self.part_of_ancestors()

    def find_all_ancs(self):
        for rel, ancs in self.ancestors.items():
            self.all_ancestors.update(ancs)

    def find_root(self, graph):
        if self.root is not None:
            return self.root
        elif len(self.is_a_ancestors(graph)) != 0:   # this concept has ancestors: which means it is not the root
            anc = next(iter(self.ancestors['is_a']))
            self.root = concept_dict[anc].find_root(graph)
            return self.root
        else:
            self.root = self.id
            return self.root


def load_concepts_to_graph(input_labelsFile, graph):
    f = open(input_labelsFile, "r")
    lines = f.readlines()
    for line in lines:
        line = line.rstrip("\n")
        tokens = line.split("\t")
        graph.add_node(tokens[0], label=tokens[1])
    f.close()
    return graph


def load_isa_relations_to_graph(input_hierarchyFile, graph):
    f = open(input_hierarchyFile, "r")
    lines = f.readlines()
    for line in lines:
        line = line.rstrip("\n")
        tokens = line.split("\t")
        if tokens[1] == 'is_a':
            graph.add_edge(tokens[0], tokens[2])
    f.close()
    return graph

#load concepts as Concept class instances
def load_concepts(id_label_file):
    global concept_dict
    concept_dict = {}
    with open(id_label_file, 'r') as txtfile:
        lines = txtfile.readlines()
        for line in lines:
            line = line.rstrip("\n")
            tokens = line.split("\t")
            concept_dict[tokens[0]] = Concept(tokens[0], tokens[1])

# load direct parent by different relations into class instances created by load_concepts() method
def load_parents(all_relations_file):
    with open(all_relations_file, 'r') as txtfile:
        lines = txtfile.readlines()
        for line in lines:
            line = line.rstrip("\n")
            tokens = line.split("\t")
            #parents = None
            if tokens[1] not in concept_dict[tokens[0]].parents:
                parents = set()
            else:
                parents = concept_dict[tokens[0]].parents[tokens[1]]
            parents.add(tokens[2])
            concept_dict[tokens[0]].parents[tokens[1]] = parents


def print_concept_info():
    for con in concept_dict.values():
        print(con.id, con.label, con.parents)


def compute_closure(labels_file, all_rels_file, noun_chunks_file, pos_tags_file):
    global graph
    graph = nx.DiGraph()
    load_concepts_to_graph(labels_file, graph)
    load_isa_relations_to_graph(all_rels_file, graph)

    load_concepts(labels_file)
    load_parents(all_rels_file)

    roots = set()
    for con in concept_dict.values():
        #print(con.id, con.label, con.parents['is_a'])
        con.find_all_ancs_closure()
        con.find_all_ancs()
        rt = con.find_root()
        roots.add(rt)
    print(roots)

    return concept_dict




def main():
    start_time = time.time()

    # global graph
    # graph = nx.DiGraph()
    # load_concepts_to_graph('inputs/GO_labels_2020_11_18.txt', graph)
    # load_isa_relations_to_graph('inputs/GO_all_relations_2020_11_18.txt', graph)
    #
    # load_concepts('inputs/GO_labels_2020_11_18.txt')
    # load_parents('inputs/GO_all_relations_2020_11_18.txt')
    #
    # #print_concept_info()
    #
    # #compute_attr_rel_closure()
    #
    # compute_part_of_closure()
    # #write_attr_rel_closure_to_file('closure/part_of_closure.csv')

    #compute_closure('inputs/GO_labels_2020_11_18.txt', 'inputs/GO_all_relations_2020_11_18.txt', 'noun_chunks/noun_chunks_en_core_web_rtf.csv')
    #multi_relations_among_concepts()

    # closure_concept_dict = compute_closure('inputs/GO_labels_2020_11_18.txt', 'inputs/GO_all_relations_2020_11_18.txt',
    #                                        'noun_chunks/noun_chunks_en_core_web_rtf_2.csv',
    #                                        'part_of_speech_tags/part_of_speech_tags_en_core_web_rtf.csv')


    end_time = (time.time() - start_time) / 60
    print("Total time: {0:.2f} mins".format(end_time))


if __name__=='__main__':
    main()


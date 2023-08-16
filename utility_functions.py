from Graph import *
from NonLatticeSubgraphs import *
from itertools import product

def identify_subconcept(subhierarchy_graph, whole_ontology_graph, output_file):
    con_subconcepts = defaultdict(set)  # key = concept, value = set of subconcepts
    for i, con1 in enumerate(subhierarchy_graph.nodes()):
        print(i)
        # if i>100:
        #     break
        con1_obj = subhierarchy_graph.nodes[con1]['data']
        con1_pref_name_modified = ' ' + con1_obj.pref_name + ' '
        for con2 in whole_ontology_graph.nodes():
            if con1 == con2:
                continue

            con2_obj = whole_ontology_graph.nodes[con2]['data']
            con2_pref_name_modified = ' ' + con2_obj.pref_name + ' '

            if con2_pref_name_modified in con1_pref_name_modified:
                con_subconcepts[con1].add(con2)

    with open(output_file, 'w') as txtfile:
        for conID, subcons in con_subconcepts.items():
            txtfile.write(conID + '\t' + ','.join(subcons) + '\n')


# looks for sub-concepts in the given subhierarchies
def identify_subconcepts_in_particular_subhierarchies(subhierarchy_graph, subhierarchy_list, output_file):
    con_subconcepts = defaultdict(set)  # key = concept, value = set of subconcepts
    for i, con1 in enumerate(subhierarchy_graph.nodes()):
        print(i)
        # if i>100:
        #     break
        con1_obj = subhierarchy_graph.nodes[con1]['data']
        con1_pref_name_modified = ' ' + con1_obj.pref_name + ' '

        for subhierarchy in subhierarchy_list:
            for con2 in subhierarchy.nodes():
                if con1 == con2:
                    continue

                con2_obj = subhierarchy.nodes[con2]['data']
                con2_pref_name_modified = ' ' + con2_obj.pref_name + ' '

                if con2_pref_name_modified in con1_pref_name_modified:
                    con_subconcepts[con1].add(con2)

    with open(output_file, 'w') as txtfile:
        for conID, subcons in con_subconcepts.items():
            txtfile.write(conID + '\t' + ','.join(subcons) + '\n')


def main():
    start_time = time.time()

    G = load_networkx_graph("inputs/SNOMED/snomed_20210301_labels_status.txt",
                            "inputs/SNOMED/snomed_20210301_hierarchy.txt")
    load_attribute_rels_to_graph(G, "inputs/SNOMED/snomed_20210301_attribute_relations.txt")

    subhierarchy_root = '373873005'  #'404684003'
    subhierarchy_graph = obtainSubhierarchy(G, subhierarchy_root)
    max_nls_size = 6  # None

    #pref_name_ids = preferredName_to_id_map("inputs/SNOMED/snomed_20210301_labels_status.txt")

    #identify_subconcept(subhierarchy_graph, G, 'inputs/SNOMED/snomed_20210301_root_373873005_subconcepts.txt')

    subhierarchy_list = []
    subhierarchy_list.append(obtainSubhierarchy(G, '105590001'))
    subhierarchy_list.append(obtainSubhierarchy(G, '736542009'))
    subhierarchy_list.append(obtainSubhierarchy(G, '767023003'))
    subhierarchy_list.append(obtainSubhierarchy(G, '277406006'))


    identify_subconcepts_in_particular_subhierarchies(subhierarchy_graph, subhierarchy_list, 'inputs/SNOMED/snomed_20210301_root_373873005_subconceptsIn4Subhierarchies.txt')

    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__":
    main()
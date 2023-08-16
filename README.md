# OQA_logical_definitions_lexical_features
 Detecting missing IS-A relations in biomedical ontologies leveraging logical definitions and lexical features

The notebook "Main pipeline.ipynb" contains the code to identify missing IS-A relations. You need 6 input files:

1. input_labelsFile_ncit - Each line contains a concept ID and a name separated by a tab.
2. input_hierarchyFile_ncit - Each line contains a child concept and a parent concept (i.e denoting a direct IS-A relation) separated by a tab.
3. input_nlsFile_ncit - Each line contains a non-lattice subgraph.
4. input_conceptStatus_ncit - Each line contains the definition status (primitive/defined) of a concept separated by a tab.
5. input_attributeFile_ncit - Each line contains an attribute relation of a concept. The concept and attribute-value pair are separated by a tab. Attribute-value pair are separated by '|'.
6. input_associationFile_ncit - Each line contains an association of a concept. The concept and association-value pair are separated by a tab. Association-value pair are separated by '|'.

Examples for these files are given in the "inputs" directory.
   

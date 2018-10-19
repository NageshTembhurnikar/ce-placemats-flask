import networkx as nx
import logging
import string
from itertools import combinations
from collections import defaultdict
from app.placemats.data.ncbi_client import get_mesh_category
from app.placemats.data.frequency_of_word_occurrences import *
from app.placemats.data.mesh_categories import mesh_categories

logger = logging.getLogger(__name__)

def hierarchical_data(edge_to_nodes: dict):
    # Creating a graph of keywords
    graph = nx.Graph()
    keywords = []
    keyword_category_dict = defaultdict()
    top_100_keywords = compute_frequent_keywords(edge_to_nodes, CUTOFF=100)

    for edges, nodes in edge_to_nodes.items():
        new_nodes = []
        for n in nodes:
            if n not in top_100_keywords:
                continue
            else:

                if n in keyword_category_dict:
                    new_nodes.append(keyword_category_dict[n])
                else:

                    if n in mesh_categories:
                        renamed_node = str(mesh_categories[n] + '.' + n.replace("."," "))

                    else:
                        logging.info('Category for %s does not exist; querying MeSH via Entrez', n)
                        category = get_mesh_category(n)
                        renamed_node = category + '.' + n.replace("."," ")
                        mesh_categories[n] = category

                    new_nodes.append(renamed_node)
                    keyword_category_dict[n] = renamed_node

                keywords.extend(new_nodes)

        for n1, n2 in combinations(new_nodes, 2):
            if graph.has_edge(n1, n2):
                graph[n1][n2]['weight'] += 1
            else:
                graph.add_edge(n1, n2, weight=1)

    co_occurences = []
    for n in graph.nodes:
        imports = {}
        neighbors = [nb for nb in graph.neighbors(n)]
        for each_neighbor in neighbors:
            weight_value = graph.get_edge_data(n, each_neighbor)
            imports[each_neighbor] = weight_value['weight']
        co_occurences.append({'name': n, 'size': keywords.count(n), 'imports': imports})
    return co_occurences
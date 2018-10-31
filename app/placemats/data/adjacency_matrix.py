import networkx as nx
import logging
from itertools import combinations

logger = logging.getLogger(__name__)


def adjacency_matrix(edge_to_nodes: dict, node_whitelist: set=None):
    """
    Builds the adjacency_matrix for the provided dict.

    :param edge_to_nodes: The value for each key is the set of nodes for which an edge should be added
        for each combination of nodes to represent the relationship denoted by the key. To use a specific example,
        the author adjacency_matrix is built by passing in a dict where the keys are PMID's and values
        are the set of authors for a given PMID.
    :param node_whitelist: Whitelist of nodes to include
    :return:
    """
    graph = nx.Graph()
    author_list = []
    for edge, nodes in edge_to_nodes.items():
        author_list.extend(nodes)
        for n1, n2 in combinations(nodes, 2):
            if node_whitelist is not None and (n1 not in node_whitelist or n2 not in node_whitelist):
                continue
            if graph.has_edge(n1, n2):
                graph[n1][n2]['weight'] += 1
            else:
                graph.add_edge(n1, n2, weight=1)
    '''
    author_publication_count = []
    # Added to count the number of publication each aouthor has
    for n in graph.nodes:
        author_publication_count.append({'name': n, 'count': author_list.count(n)})
    '''
    nodes = []
    node_to_index = {}
    idx = 0
    for n in graph.nodes:
        nodes.append({'name': n, 'group': 1})
        node_to_index[n] = idx
        idx += 1
    links = []
    for n1, n2, weight in graph.edges(data='weight'):
        links.append({
            'source': node_to_index[n1],
            'target': node_to_index[n2],
            'value': weight,
        })

    #return {
    #    'nodes': nodes,
    #    'links': links,
    #    'publication_counts': author_publication_count
    #}

    return {
        'nodes': nodes,
        'links': links}


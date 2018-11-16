import logging

logger = logging.getLogger(__name__)


def adjacency_matrix_for_one(edge_to_nodes: dict):

    nodes, links = [], []
    author_name = ''.join(list(edge_to_nodes.values())[0])
    nodes.append({'name': ''.join(list(edge_to_nodes.values())[0]), 'group': 1})
    links.append({
        'source': author_name,
        'target': author_name,
        'value': len(edge_to_nodes.values())
    })

    return {
            'nodes': nodes,
            'links': links}
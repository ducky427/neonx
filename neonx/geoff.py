# -*- coding: utf-8 -*-

import json

import networkx as nx


__all__ = ['get_geoff']


def get_node(node_name, properties, encoder):
    if properties:
        return '({0} {1})'.format(node_name,
                                  encoder.encode(properties))
    else:
        return '({0})'.format(node_name)


def get_edge(from_node, to_node, properties, edge_relationship_name, encoder):
    edge_string = None
    if properties:
        args = [from_node, edge_relationship_name,
                encoder.encode(properties), to_node]
        edge_string = '({0})-[:{1} {2}]->({3})'.format(*args)
    else:
        args = [from_node, edge_relationship_name, to_node]
        edge_string = '({0})-[:{1}]->({2})'.format(*args)

    return edge_string


def get_geoff(graph, edge_rel_name, encoder=None):
    """ Get the `graph` as Geoff string. The edges between the nodes
    have relationship name `edge_rel_name`. The code
    below shows a simple example::

        from neonx import get_geoff

        # create a graph
        import networkx as nx
        G = nx.Graph()
        G.add_nodes_from([1, 2, 3])
        G.add_edge(1, 2)
        G.add_edge(2, 3)


        # get the geoff string
        geoff_string = get_geoff(G, 'LINKS_TO')

    If the properties are not json encodable, please pass a custom JSON encoder
    class. See `JSONEncoder
    <http://docs.python.org/2/library/json.html#json.JSONEncoder/>`_.

    :param graph: A NetworkX Graph or a DiGraph
    :param edge_rel_name: Relationship name between the nodes
    :param optional encoder: JSONEncoder object. Defaults to JSONEncoder.
    :rtype: A Geoff string
    """

    if encoder is None:
        encoder = json.JSONEncoder()
    is_digraph = isinstance(graph, nx.DiGraph)

    lines = []
    lapp = lines.append
    for node_name, properties in graph.nodes(data=True):
        lapp(get_node(node_name, properties, encoder))

    for from_node, to_node, properties in graph.edges(data=True):
        lapp(get_edge(from_node, to_node, properties, edge_rel_name, encoder))
        if not is_digraph:
            lapp(get_edge(to_node, from_node, properties, edge_rel_name,
                          encoder))

    return '\n'.join(lines)

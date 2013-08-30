# -*- coding: utf-8 -*-

import json

import networkx as nx
import requests

__all__ = ['write_to_neo']


JSON_CONTENT_TYPE = 'application/json; charset=UTF-8'


def get_node(node_id, properties):
    return {"method": "POST",
            "to": "/node",
            "id": node_id,
            "body": properties}


def get_relationship(from_id, to_id, rel_name, properties):
    body = {"to": "{{{0}}}".format(to_id), "type": rel_name,
            "data": properties}

    return {"method": "POST",
            "to": "{{{0}}}/relationships".format(from_id),
            "body": body}


def generate_data(graph, edge_rel_name, encoder):
    is_digraph = isinstance(graph, nx.DiGraph)
    entities = []
    nodes = {}

    for i, (node_name, properties) in enumerate(graph.nodes(data=True)):
        entities.append(get_node(i, properties))
        nodes[node_name] = i

    for from_node, to_node, properties in graph.edges(data=True):
        edge = get_relationship(nodes[from_node], nodes[to_node],
                                edge_rel_name, properties)
        entities.append(edge)

        if not is_digraph:
            reverse_edge = get_relationship(nodes[to_node],
                                            nodes[from_node],
                                            edge_rel_name, properties)
            entities.append(reverse_edge)

    return encoder.encode(entities)


def write_to_neo(server_url, graph, edge_rel_name, encoder=None):
    """Write the `graph` as Geoff string. The edges between the nodes
    have relationship name `edge_rel_name`. The code
    below shows a simple example::

        from neonx import write_to_neo

        # create a graph
        import networkx as nx
        G = nx.Graph()
        G.add_nodes_from([1, 2, 3])
        G.add_edge(1, 2)
        G.add_edge(2, 3)


        # save graph to neo4j
        results = write_to_neo("http://localhost:7474/db/data/", G, 'LINKS_TO')

    If the properties are not json encodable, please pass a custom JSON encoder
    class. See `JSONEncoder
    <http://docs.python.org/2/library/json.html#json.JSONEncoder/>`_.

    :param server_url: Server URL for the Neo4j server.
    :param graph: A NetworkX Graph or a DiGraph
    :param edge_rel_name: Relationship name between the nodes
    :param optional encoder: JSONEncoder object. Defaults to JSONEncoder.
    :rtype: A list of Neo4j created resources.
    """

    if encoder is None:
        encoder = json.JSONEncoder()

    all_server_urls = requests.get(server_url).json()
    batch_url = all_server_urls['batch']

    data = generate_data(graph, edge_rel_name, encoder)
    headers = {'content-type': JSON_CONTENT_TYPE}
    result = requests.post(batch_url, data=data, headers=headers)

    if result.status_code != 200:
        if result.headers.get('content-type') == JSON_CONTENT_TYPE:
            result_json = result.json()
            e = Exception(result_json['exception'])
            e.args += (result_json['stacktrace'], )
        else:
            e = Exception("Unknown server error.")
            e.args += (result.content, )
        raise e

    return result.json()

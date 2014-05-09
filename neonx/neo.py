
# -*- coding: utf-8 -*-

import json

import networkx as nx
import requests

__all__ = ['write_to_neo', 'get_neo_graph']


JSON_CONTENT_TYPE = 'application/json; charset=utf-8'
HEADERS = {'content-type': JSON_CONTENT_TYPE}


def get_node(node_id, properties):
    """reformats a NetworkX node for `generate_data()`.

    :param node_id: the index of a NetworkX node
    :param properties: a dictionary of node attributes
    :rtype: a dictionary representing a Neo4j POST request
    """
    return {"method": "POST",
            "to": "/node",
            "id": node_id,
            "body": properties}


def get_relationship(from_id, to_id, rel_name, properties):
    """reformats a NetworkX edge for `generate_data()`.

    :param from_id: the ID of a NetworkX source node
    :param to_id: the ID of a NetworkX target node
    :param rel_name: string that describes the relationship between the
        two nodes
    :param properties: a dictionary of edge attributes
    :rtype: a dictionary representing a Neo4j POST request
    """
    body = {"to": "{{{0}}}".format(to_id), "type": rel_name,
            "data": properties}

    return {"method": "POST",
            "to": "{{{0}}}/relationships".format(from_id),
            "body": body}


def get_label(i, label):
    """adds a label to the given (Neo4j) node.

    :param i: the index of a NetworkX node
    :param label: the label to be added to the node
    :rtype: a dictionary representing a Neo4j POST request
    """
    return {"method": "POST",
            "to": "{{{0}}}/labels".format(i),
            "body": label}


def generate_data(graph, edge_rel_name, label, encoder):
    """converts a NetworkX graph into a format that can be uploaded to
    Neo4j using a single HTTP POST request.

    :rtype: a JSON encoded string for `Neo4j batch operations \
    <http://docs.neo4j.org/chunked/stable/rest-api-batch-ops.html>_`.

    :param graph: A NetworkX Graph or a DiGraph
    :param edge_rel_name: string that describes the relationship between
        the two nodes
    :param label: an optional label to be added to all nodes
    :param encoder: a JSONEncoder object
    """
    is_digraph = isinstance(graph, nx.DiGraph)
    entities = []
    nodes = {}

    for i, (node_name, properties) in enumerate(graph.nodes(data=True)):
        entities.append(get_node(i, properties))
        nodes[node_name] = i

    if label:
        for i in nodes.values():
            entities.append(get_label(i, label))

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


def check_exception(result):
    """checks, if the preceding HTTP request was accepted by the Neo4j
    server.

    :param result: a `Response \
<http://docs.python-requests.org/en/latest/api/#requests.Response>`_
        instance.
    :rtype: an Exception or None
    """
    if result.status_code == 200:
        return

    if result.headers.get('content-type', '').lower() == JSON_CONTENT_TYPE:
        result_json = result.json()
        e = Exception(result_json['exception'])
        e.args += (result_json['stacktrace'], )
    else:
        e = Exception("Unknown server error.")
        e.args += (result.content, )
    raise e


def get_server_urls(server_url):
    """connects to the server with a GET request and returns its answer
    (e.g. a number of URLs of REST endpoints, the server version etc.)
    as a dictionary.
    
    :param server_url: the URL of the Neo4j server
    :rtype: a dictionary of parameters of the Neo4j server
    """
    result = requests.get(server_url)
    check_exception(result)
    return result.json()


def write_to_neo(server_url, graph, edge_rel_name, label=None,
                 encoder=None):
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
        results = write_to_neo("http://localhost:7474/db/data/", G, \
'LINKS_TO', 'Node')

    If the properties are not json encodable, please pass a custom JSON
    encoder class. See `JSONEncoder
    <http://docs.python.org/2/library/json.html#json.JSONEncoder/>`_.

    If `label` is present, this label was be associated with all the nodes
    created. Label support were added in Neo4j 2.0. See \
    `here <http://bit.ly/1fo5324>`_.

    :param server_url: Server URL for the Neo4j server.
    :param graph: A NetworkX Graph or a DiGraph.
    :param edge_rel_name: Relationship name between the nodes.
    :param optional label: It will add this label to the node. \
See `here <http://bit.ly/1fo5324>`_.
    :param optional encoder: JSONEncoder object. Defaults to JSONEncoder.
    :rtype: A list of Neo4j created resources.
    """

    if encoder is None:
        encoder = json.JSONEncoder()

    all_server_urls = get_server_urls(server_url)
    batch_url = all_server_urls['batch']

    data = generate_data(graph, edge_rel_name, label, encoder)
    result = requests.post(batch_url, data=data, headers=HEADERS)
    check_exception(result)
    return result.json()


LABEL_QRY = """MATCH (a:{0})-[r]->(b:{1}) RETURN ID(a), r, ID(b);"""


def get_neo_graph(server_url, label):
    """Return a graph of all nodes with a given Neo4j label and edges between
    the same nodes.

    :param server_url: Server URL for the Neo4j server.
    :param label: The label to retrieve the nodes for.
    :rtype: A `Digraph \
<http://networkx.github.io/documentation/latest/\
reference/classes.digraph.html>`_.
    """

    all_server_urls = get_server_urls(server_url)
    batch_url = all_server_urls['batch']

    data = [{"method": "GET", "to": '/label/{0}/nodes'.format(label),
             "body": {}},
            {"method": "POST", "to": '/cypher', "body": {"query":
             LABEL_QRY.format(label, label), "params": {}}},
            ]

    result = requests.post(batch_url, data=json.dumps(data), headers=HEADERS)
    check_exception(result)

    node_data, edge_date = result.json()
    graph = nx.DiGraph()

    for n in node_data['body']:
        node_id = int(n['self'].rpartition('/')[-1])
        graph.add_node(node_id, **n['data'])

    for n in edge_date['body']['data']:
        from_node_id, relationship, to_node_id = n

        properties = relationship['data']
        properties['neo_rel_name'] = relationship['type']
        graph.add_edge(from_node_id, to_node_id, **properties)

    return graph

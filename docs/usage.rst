========
Usage
========

To use NetworkX to Neo4j in a project::

    import neonx

To covert a Networkx graph to a Geoff string::

    # create a Networkx graph
    # LINKS_TO is the relatioship name between the nodes
    data = neonx.get_geoff(graph, "LINKS_TO")

It is assumed that the all the properties for the nodes are edges are
json encodable. If they are not, please extend
`JSONEncoder <http://docs.python.org/2/library/json.html#json.JSONEncoder>`_.
For example, if you want to encode python date objects as well the usual types::

    import json
    import datetime

    class DateEncoder(json.JSONEncoder):

        def default(self, o):
            if isinstance(o, datetime.date):
                return o.strftime('%Y-%m-%d')
            return json.JSONEncoder.default(self, o)

    data = neonx.get_geoff(graph, "LINKS_TO", DateEncoder())

To upload the graph to neo4j server hosted on localhost::

    results = neonx.write_to_neo("http://localhost:7474/db/data/", graph, 'LINKS_TO')

Again, it is assumed that the properties of the graph are json encodable.
If not, please pass a custom encoder in a similar way to the example above.
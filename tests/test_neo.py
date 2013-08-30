# -*- coding: utf-8 -*-

"""
test_neo
----------------------------------

Tests for `neo` module.
"""

import json
import unittest

from neonx.neo import generate_data, write_to_neo

import httpretty
import networkx as nx


BATCH_URL = '{"batch":"http://localhost:7474/db/data/batch"}'


class TestGenerateNeoData(unittest.TestCase):

    @httpretty.activate
    def test_get_geoff_digraph(self):
        truth = """[{"body": {}, "to": "/node", "method": "POST", "id": 0}, {"body": {}, "to": "/node", "method": "POST", "id": 1}, {"body": {"debug": "test"}, "to": "/node", "method": "POST", "id": 2}, {"body": {"to": "{1}", "type": "LINK_TO", "data": {"debug": false}}, "to": "{0}/relationships", "method": "POST"}, {"body": {"to": "{2}", "type": "LINK_TO", "data": {}}, "to": "{0}/relationships", "method": "POST"}]"""

        graph = nx.balanced_tree(2, 1, create_using=nx.DiGraph())
        graph.node[2]['debug'] = 'test'
        graph[0][1]['debug'] = False
        result = generate_data(graph, "LINK_TO", json.JSONEncoder())
        self.assertEqual(json.loads(result), json.loads(truth))

        httpretty.register_uri(httpretty.GET,
                               "http://localhost:7474/db/data/",
                               body=BATCH_URL)

        httpretty.register_uri(httpretty.POST,
                               "http://localhost:7474/db/data/batch",
                               body='["Dummy"]')

        result = write_to_neo("http://localhost:7474/db/data/", graph,
                              "LINKS_TO")
        self.assertEqual(result, ["Dummy"])

    @httpretty.activate
    def test_get_geoff_graph(self):
        truth = """[{"body": {}, "to": "/node", "method": "POST", "id": 0}, {"body": {}, "to": "/node", "method": "POST", "id": 1}, {"body": {"debug": "test"}, "to": "/node", "method": "POST", "id": 2}, {"body": {"to": "{1}", "type": "LINK_TO", "data": {"debug": false}}, "to": "{0}/relationships", "method": "POST"}, {"body": {"to": "{0}", "type": "LINK_TO", "data": {"debug": false}}, "to": "{1}/relationships", "method": "POST"}, {"body": {"to": "{2}", "type": "LINK_TO", "data": {}}, "to": "{0}/relationships", "method": "POST"}, {"body": {"to": "{0}", "type": "LINK_TO", "data": {}}, "to": "{2}/relationships", "method": "POST"}]"""

        graph = nx.balanced_tree(2, 1)
        graph.node[2]['debug'] = 'test'
        graph[0][1]['debug'] = False
        result = generate_data(graph, "LINK_TO", json.JSONEncoder())
        self.assertEqual(json.loads(result), json.loads(truth))

        httpretty.register_uri(httpretty.GET,
                               "http://localhost:7474/db/data/",
                               body=BATCH_URL)

        httpretty.register_uri(httpretty.POST,
                               "http://localhost:7474/db/data/batch",
                               body='["Dummy"]')

        result = write_to_neo("http://localhost:7474/db/data/", graph,
                              "LINKS_TO")
        self.assertEqual(result, ["Dummy"])

    @httpretty.activate
    def test_failure_500(self):
        graph = nx.balanced_tree(2, 1)

        httpretty.register_uri(httpretty.GET,
                               "http://localhost:7474/db/data/",
                               body=BATCH_URL)

        httpretty.register_uri(httpretty.POST,
                               "http://localhost:7474/db/data/batch",
                               body='Server Error', status=500,
                               content_type='text/html')

        self.assertRaises(Exception, lambda: write_to_neo("http://localhost:7474/db/data/", graph, 'LINK_TO'))

    @httpretty.activate
    def test_failure_json(self):
        graph = nx.balanced_tree(2, 1)

        httpretty.register_uri(httpretty.GET,
                               "http://localhost:7474/db/data/",
                               body=BATCH_URL)

        httpretty.register_uri(httpretty.POST,
                               "http://localhost:7474/db/data/batch",
                               body='{"exception": "Error", "stacktrace": "-----"}', status=500,
                               content_type='application/json; charset=UTF-8')

        self.assertRaises(Exception, lambda: write_to_neo("http://localhost:7474/db/data/", graph, 'LINK_TO'))

if __name__ == '__main__':
    unittest.main()

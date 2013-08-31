
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
        truth = [{'body': {}, 'id': 0, 'method': 'POST', 'to': '/node'},
                 {'body': {}, 'id': 1, 'method': 'POST', 'to': '/node'},
                 {'body': {'debug': 'test'}, 'id': 2, 'method': 'POST',
                  'to': '/node'},
                 {'body': "ITEM", 'method': 'POST', 'to': '{0}/labels'},
                 {'body': "ITEM", 'method': 'POST', 'to': '{1}/labels'},
                 {'body': "ITEM", 'method': 'POST', 'to': '{2}/labels'},
                 {'body': {'data': {'debug': False}, 'to': '{1}',
                  'type': 'LINK_TO'},
                  'method': 'POST', 'to': '{0}/relationships'},
                 {'body': {'data': {}, 'to': '{2}', 'type': 'LINK_TO'},
                  'method': 'POST',
                  'to': '{0}/relationships'}]

        graph = nx.balanced_tree(2, 1, create_using=nx.DiGraph())
        graph.node[2]['debug'] = 'test'
        graph[0][1]['debug'] = False
        result = generate_data(graph, "LINK_TO", "ITEM", json.JSONEncoder())
        self.assertEqual(json.loads(result), truth)

        httpretty.register_uri(httpretty.GET,
                               "http://localhost:7474/db/data/",
                               body=BATCH_URL)

        httpretty.register_uri(httpretty.POST,
                               "http://localhost:7474/db/data/batch",
                               body='["Dummy"]')

        result = write_to_neo("http://localhost:7474/db/data/", graph,
                              "LINKS_TO", "ITEM")

        self.assertEqual(result, ["Dummy"])

    @httpretty.activate
    def test_get_geoff_graph(self):
        truth = [{'body': {}, 'id': 0, 'method': 'POST', 'to': '/node'},
                 {'body': {}, 'id': 1, 'method': 'POST', 'to': '/node'},
                 {'body': {'debug': 'test'}, 'id': 2, 'method': 'POST',
                  'to': '/node'},
                 {'body': "ITEM", 'method': 'POST', 'to': '{0}/labels'},
                 {'body': "ITEM", 'method': 'POST', 'to': '{1}/labels'},
                 {'body': "ITEM", 'method': 'POST', 'to': '{2}/labels'},
                 {'body': {'data': {'debug': False}, 'to': '{1}',
                  'type': 'LINK_TO'},
                  'method': 'POST', 'to': '{0}/relationships'},
                 {'body': {'data': {'debug': False}, 'to': '{0}',
                  'type': 'LINK_TO'},
                  'method': 'POST', 'to': '{1}/relationships'},
                 {'body': {'data': {}, 'to': '{2}', 'type': 'LINK_TO'},
                  'method': 'POST', 'to': '{0}/relationships'},
                 {'body': {'data': {}, 'to': '{0}', 'type': 'LINK_TO'},
                  'method': 'POST', 'to': '{2}/relationships'}]

        graph = nx.balanced_tree(2, 1)
        graph.node[2]['debug'] = 'test'
        graph[0][1]['debug'] = False
        result = generate_data(graph, "LINK_TO", "ITEM", json.JSONEncoder())
        self.assertEqual(json.loads(result), truth)

        httpretty.register_uri(httpretty.GET,
                               "http://localhost:7474/db/data/",
                               body=BATCH_URL)

        httpretty.register_uri(httpretty.POST,
                               "http://localhost:7474/db/data/batch",
                               body='["Dummy"]')

        result = write_to_neo("http://localhost:7474/db/data/", graph,
                              "LINKS_TO", "ITEM")
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

        f = lambda: write_to_neo("http://localhost:7474/db/data/",
                                 graph, 'LINK_TO', "ITEM")
        self.assertRaises(Exception, f)

    @httpretty.activate
    def test_failure_json(self):
        graph = nx.balanced_tree(2, 1)

        httpretty.register_uri(httpretty.GET,
                               "http://localhost:7474/db/data/",
                               body=BATCH_URL)

        httpretty.register_uri(httpretty.POST,
                               "http://localhost:7474/db/data/batch",
                               body='{"exception": "Error", "stacktrace": 1}',
                               status=500,
                               content_type='application/json; charset=UTF-8')

        f = lambda: write_to_neo("http://localhost:7474/db/data/",
                                 graph, 'LINK_TO')
        self.assertRaises(Exception, f)

if __name__ == '__main__':
    unittest.main()

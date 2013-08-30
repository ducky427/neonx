# -*- coding: utf-8 -*-

"""
test_geoff
----------------------------------

Tests for `geoff` module.
"""

import datetime
import json
import unittest

from neonx import get_geoff

import networkx as nx


class TestGetGeoff(unittest.TestCase):

    def test_get_geoff_digraph(self):
        result = """(0)
(1)
(2 {"debug": "test\\""})
(0)-[:LINK_TO {"debug": false}]->(1)
(0)-[:LINK_TO]->(2)"""
        graph = nx.balanced_tree(2, 1, create_using=nx.DiGraph())
        graph.node[2]['debug'] = 'test"'
        graph[0][1]['debug'] = False
        self.assertEqual(get_geoff(graph, 'LINK_TO'), result)

    def test_get_geoff_graph(self):
        result = """(0)
(1)
(2 {"debug": "test\\""})
(0)-[:LINK_TO {"debug": false}]->(1)
(1)-[:LINK_TO {"debug": false}]->(0)
(0)-[:LINK_TO]->(2)
(2)-[:LINK_TO]->(0)"""
        graph = nx.balanced_tree(2, 1)
        graph.node[2]['debug'] = 'test"'
        graph[0][1]['debug'] = False
        self.assertEqual(get_geoff(graph, 'LINK_TO'), result)


class DateEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime.date):
            return o.strftime('%Y-%m-%d')
        return json.JSONEncoder.default(self, o)


class TestGetGeoffDate(unittest.TestCase):

    def test_get_geoff_digraph(self):
        today = datetime.date(2012, 1, 1)

        graph = nx.balanced_tree(2, 1, create_using=nx.DiGraph())
        graph.node[2]['debug'] = 'test"'
        graph[0][1]['debug'] = today

        self.assertRaises(TypeError, get_geoff, (graph, 'LINK_TO'))

    def test_get_geoff_digraph_custom(self):
        today = datetime.date(2012, 1, 1)
        result = """(0)
(1)
(2 {"debug": "test\\""})
(0)-[:LINK_TO {"debug": "2012-01-01"}]->(1)
(0)-[:LINK_TO]->(2)"""
        graph = nx.balanced_tree(2, 1, create_using=nx.DiGraph())
        graph.node[2]['debug'] = 'test"'
        graph[0][1]['debug'] = today

        data = get_geoff(graph, 'LINK_TO', DateEncoder())
        self.assertEqual(data, result)

if __name__ == '__main__':
    unittest.main()

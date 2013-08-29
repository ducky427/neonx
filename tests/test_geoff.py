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
(3)
(4)
(5)
(6)
(0)-[:LINK_TO {"debug": false}]->(1)
(0)-[:LINK_TO]->(2)
(1)-[:LINK_TO]->(3)
(1)-[:LINK_TO]->(4)
(2)-[:LINK_TO]->(5)
(2)-[:LINK_TO]->(6)"""
        graph = nx.balanced_tree(2, 2, create_using=nx.DiGraph())
        graph.node[2]['debug'] = 'test"'
        graph[0][1]['debug'] = False
        self.assertEqual(get_geoff(graph, 'LINK_TO'), result)

    def test_get_geoff_graph(self):
        result = """(0)
(1)
(2 {"debug": "test\\""})
(3)
(4)
(5)
(6)
(0)-[:LINK_TO {"debug": false}]->(1)
(1)-[:LINK_TO {"debug": false}]->(0)
(0)-[:LINK_TO]->(2)
(2)-[:LINK_TO]->(0)
(1)-[:LINK_TO]->(3)
(3)-[:LINK_TO]->(1)
(1)-[:LINK_TO]->(4)
(4)-[:LINK_TO]->(1)
(2)-[:LINK_TO]->(5)
(5)-[:LINK_TO]->(2)
(2)-[:LINK_TO]->(6)
(6)-[:LINK_TO]->(2)"""
        graph = nx.balanced_tree(2, 2)
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

        graph = nx.balanced_tree(2, 2, create_using=nx.DiGraph())
        graph.node[2]['debug'] = 'test"'
        graph[0][1]['debug'] = today

        self.assertRaises(TypeError, get_geoff, (graph, 'LINK_TO'))

    def test_get_geoff_digraph_custom(self):
        today = datetime.date(2012, 1, 1)
        result = """(0)
(1)
(2 {"debug": "test\\""})
(3)
(4)
(5)
(6)
(0)-[:LINK_TO {"debug": "2012-01-01"}]->(1)
(0)-[:LINK_TO]->(2)
(1)-[:LINK_TO]->(3)
(1)-[:LINK_TO]->(4)
(2)-[:LINK_TO]->(5)
(2)-[:LINK_TO]->(6)"""
        graph = nx.balanced_tree(2, 2, create_using=nx.DiGraph())
        graph.node[2]['debug'] = 'test"'
        graph[0][1]['debug'] = today

        data = get_geoff(graph, 'LINK_TO', DateEncoder())
        self.assertEqual(data, result)

if __name__ == '__main__':
    unittest.main()

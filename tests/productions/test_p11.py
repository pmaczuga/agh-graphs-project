import unittest
from random import choice
from networkx import Graph
from matplotlib import pyplot
from agh_graphs.productions.p11 import P11
from agh_graphs.visualize import visualize_graph_3d, visualize_graph_layer


class P11Test(unittest.TestCase):
    def testCorrectGraph(self):
        graph = createCorrectGraph()

        original_positions = dict(map(lambda x: (x[0], x[1]['position']), graph.nodes(data=True)))

        prod_input = [x for x, y in graph.nodes(data=True) if y['label'] == 'i' or y['label'] == 'I']
        output = P11().apply(graph, prod_input)

        self.assertEqual(output, [])

        for node in nodes_after_merge():
            self.assertTrue(graph.has_node(node))

        for node in set(required_nodes()) - set(nodes_after_merge()):
            self.assertFalse(graph.has_node(node))

        for edge in edges_after_merge():
            self.assertTrue(graph.has_edge(edge[0], edge[1]))

        for edge in set(required_edges()) - set(edges_after_merge()):
            self.assertFalse(graph.has_edge(edge[0], edge[1]))
        #
        # check proper layers
        upper_layer_nodes = ['e01', 'e02', 'i1', 'i2']
        lower_layer_nodes = ['I1', 'I2', 'I3', 'e11', 'e12', 'e13']

        upper_layer_numbers = \
            list(map(lambda x: x[1]['layer'], filter(lambda x: x[0] in upper_layer_nodes, graph.nodes(data=True))))
        lower_layer_numbers = \
            list(map(lambda x: x[1]['layer'], filter(lambda x: x[0] in lower_layer_nodes, graph.nodes(data=True))))

        self.assertEqual(len(set(upper_layer_numbers)), 1)
        self.assertEqual(len(set(lower_layer_numbers)), 1)

        self.assertEqual(upper_layer_numbers[0] + 1, lower_layer_numbers[0])

        after_merge_positions = dict(map(lambda x: (x[0], x[1]['position']), graph.nodes(data=True)))

        for node, position in after_merge_positions.items():
            self.assertTrue(position, original_positions[node])

    def testMissingNodeGraph(self):
        for node in required_nodes():
            graph = createCorrectGraph()
            graph.remove_node(node)
            prod_input = [x for x, y in graph.nodes(data=True) if y['label'] == 'i' or y['label'] == 'I']

            with self.assertRaises(ValueError):
                P11().apply(graph, prod_input)

        for node in not_required_nodes():
            graph = createCorrectGraph()
            graph.remove_node(node)
            prod_input = [x for x, y in graph.nodes(data=True) if y['label'] == 'i' or y['label'] == 'I']
            P11().apply(graph, prod_input)

    def testMissingEdgeGraph(self):
        for edge in required_edges():
            graph = createCorrectGraph()
            graph.remove_edge(edge[0], edge[1])
            prod_input = [x for x, y in graph.nodes(data=True) if y['label'] == 'i' or y['label'] == 'I']

            with self.assertRaises(ValueError):
                P11().apply(graph, prod_input)

        for edge in not_required_edges():
            graph = createCorrectGraph()
            graph.remove_edge(edge[0], edge[1])
            prod_input = [x for x, y in graph.nodes(data=True) if y['label'] == 'i' or y['label'] == 'I']

            P11().apply(graph, prod_input)

    def testBadInput(self):
        graph = createCorrectGraph()
        prod_input = [x for x, y in graph.nodes(data=True) if y['label'] == 'i' or y['label'] == 'I']
        attributes = [y for x, y in graph.nodes(data=True) if y['label'] == 'i' or y['label'] == 'I']
        attributes[0]['label'] = 'E'
        with self.assertRaises(ValueError):
            P11().apply(graph, prod_input)

    def testBadPosition(self):
        merger_nodes = ['e13', 'e14']
        for node in merger_nodes:
            graph = createCorrectGraph()
            prod_input = [x for x, y in graph.nodes(data=True) if y['label'] == 'i' or y['label'] == 'I']

            node = list(filter(lambda x: x[0] == node, graph.nodes(data=True)))[0]
            node[1]['position'] = (1000.0, 1000.0)

            with self.assertRaises(ValueError):
                P11().apply(graph, prod_input)


def required_nodes():
    return [
        "e01",
        "e02",
        "i1",
        "i2",
        "I1",
        "I2",
        "I3",
        "e11",
        "e12",
        "e13",
        "e14",
    ]


def not_required_nodes():
    return []


def nodes_after_merge():
    # SHOULD MERGE e14 into e13
    return [
        "e01",
        "e02",
        "i1",
        "i2",
        "I1",
        "I2",
        "I3",
        "e11",
        "e12",
        "e13",
    ]


def required_edges():
    return [
        ('e01', 'i1'),
        ('e01', 'i2'),
        ('e02', 'i1'),
        ('e02', 'i2'),
        ('e01', 'e02'),
        ('i1', 'I1'),
        ('i1', 'I2'),
        ('i2', 'I3'),
        ('e11', 'I1'),
        ('e11', 'e12'),
        ('I1', 'e12'),
        ('e12', 'I2'),
        ('e12', 'e13'),
        ('I2', 'e13'),
        ('e13', 'e14'),
        ('e13', 'I3'),
        ('e14', 'I3')]


def not_required_edges():
    return []


def edges_after_merge():
    # SHOULD MERGE e14 into e13
    return [
        ('e01', 'i1'),
        ('e01', 'i2'),
        ('e02', 'i1'),
        ('e02', 'i2'),
        ('e01', 'e02'),
        ('i1', 'I1'),
        ('i1', 'I2'),
        ('i2', 'I3'),
        ('e11', 'I1'),
        ('e11', 'e12'),
        ('I1', 'e12'),
        ('e12', 'I2'),
        ('e12', 'e13'),
        ('I2', 'e13'),
        ('e13', 'I3')]

def createCorrectGraph():
    graph = Graph()
    e01 = "e01"
    e02 = "e02"
    i1 = "i1"
    i2 = "i2"

    I1 = "I1"
    I2 = "I2"
    I3 = "I3"

    e11 = "e11"
    e12 = "e12"
    e13 = "e13"
    e14 = "e14"

    graph.add_node(e01, layer=0, position=(0.0, 0.0), label='E')
    graph.add_node(e02, layer=0, position=(2.0, 2.0), label='E')
    graph.add_node(i2, layer=0, position=(0.0, 2.0), label='i')
    graph.add_node(i1, layer=0, position=(2.0, 0.0), label='i')

    graph.add_node(I1, layer=1, position=(0.0, 1.0), label='I')
    graph.add_node(I2, layer=1, position=(1.0, 2.0), label='I')
    graph.add_node(I3, layer=1, position=(2.0, 0.0), label='I')
    graph.add_node(e11, layer=1, position=(0.0, 0.0), label='E')
    graph.add_node(e12, layer=1, position=(1.0, 1.0), label='E')
    graph.add_node(e13, layer=1, position=(2.0, 2.0), label='E')
    graph.add_node(e14, layer=1, position=(0.0, 0.0), label='E')

    # upper layer edges
    graph.add_edge(e01, i1)
    graph.add_edge(e01, i2)
    graph.add_edge(e02, i1)
    graph.add_edge(e02, i2)
    graph.add_edge(e01, e02)

    # interlayer connections
    graph.add_edge(i1, I1)
    graph.add_edge(i1, I2)
    graph.add_edge(i2, I3)

    # lower layer connections
    graph.add_edge(e11, I1)
    graph.add_edge(e11, e12)

    graph.add_edge(I1, e12)

    graph.add_edge(e12, I2)
    graph.add_edge(e12, e13)

    graph.add_edge(I2, e13)

    graph.add_edge(e13, e14)
    graph.add_edge(e13, I3)
    graph.add_edge(e14, I3)

    return graph

from typing import List

from networkx import Graph
from agh_graphs.production import Production
from agh_graphs.utils import get_neighbors_at, find_overlapping_vertices, join_overlapping_vertices, get_common_neighbors


class P11(Production):

    def apply(self, graph: Graph, prod_input: List[str], orientation: int = 0, **kwargs) -> List[str]:
        """
        Apply 11th production on graph

        `prod_input` is list of 5 interiors as follows: `[upper, upper, lower, lower, lower]`,
        where `upper` is vertex on upper layer and `lower` on lower layer. Order of vertices in one
        layer is irrelevant.

        `orientation` and `**kwargs` are ignored

        Returns empty list, as no new vertices were added.
        """

        self.__check_prod_input(graph, prod_input)

        up_layer = graph.nodes()[prod_input[0]]['layer']
        down_layer = graph.nodes()[prod_input[2]]['layer']
        v1_up, v2_up = get_common_neighbors(graph, prod_input[0], prod_input[1], up_layer)
        pos_v1 = graph.nodes()[v1_up]['position']
        pos_v2 = graph.nodes()[v2_up]['position']

        x = (pos_v1[0] + pos_v2[0]) / 2
        y = (pos_v1[1] + pos_v2[1]) / 2
        pos_center = (x, y)

        to_merge = [[], []]
        for interior in prod_input[2:]:
            for v in get_neighbors_at(graph, interior, down_layer):
                if graph.nodes()[v]['position'] == pos_v1:
                    to_merge[0].append(v)
                elif graph.nodes()[v]['position'] == pos_v2:
                    to_merge[1].append(v)

        for vs in to_merge:
            if vs[0] != vs[1]:
                join_overlapping_vertices(graph, vs[0], vs[1], down_layer)

        return []

    @staticmethod
    def __check_prod_input(graph: Graph, prod_input: List[str]):

        # Check number of vertices delivered
        if len(set(prod_input)) != 5:
            raise ValueError('Too few interiors in pord_input (6 required)')

        # Check layers
        up_layer = graph.nodes()[prod_input[0]]['layer']
        down_layer = graph.nodes()[prod_input[2]]['layer']
        if any(graph.nodes()[interior]['layer'] != up_layer for interior in prod_input[:2]):
            raise ValueError('First two interior are not in the same layer')
        if any(graph.nodes()[interior]['layer'] != down_layer for interior in prod_input[2:]):
            raise ValueError('Three last interiors are not in the same layer')
        if up_layer + 1 != down_layer:
            raise ValueError('Upper layer is not right above lower one')

        # Check delivered vertices labels
        if any(graph.nodes()[interior]['label'] != 'i' for interior in prod_input[:2]):
            raise ValueError('First two interior don not have "i" label')
        if any(graph.nodes()[interior]['label'] != 'I' for interior in prod_input[2:]):
            raise ValueError('Four last interior don not have "I" label')

        # Check connections between delivered vertices
        neighbors_in_lower_layer = {prod_input[0]: set(), prod_input[1]: set()}
        for upper_interior in prod_input[:2]:
            for bottom_neighbor in get_neighbors_at(graph, upper_interior, down_layer):
                neighbors_in_lower_layer[upper_interior].add(bottom_neighbor)
        for lower_interior in prod_input[2:]:
            if lower_interior not in neighbors_in_lower_layer[prod_input[0]]\
              and lower_interior not in neighbors_in_lower_layer[prod_input[1]]:
                raise ValueError('Upper interiors not connected properly to lower ones')

        # maps lower interiors to its parent in upper layer
        lower_to_upper = dict()
        for upper in neighbors_in_lower_layer:
            for lower in neighbors_in_lower_layer[upper]:
                lower_to_upper[lower] = upper

        # Check common neighbors of upper interiors
        upper_neighbors = get_common_neighbors(graph, prod_input[0], prod_input[1], up_layer)
        if len(upper_neighbors) != 2:
            raise ValueError('Upper interiors do not have 2 common neighbors')

        # Get those neighbors and their positions as well as center position between them
        v1_up, v2_up = upper_neighbors
        pos_v1 = graph.nodes()[v1_up]['position']
        pos_v2 = graph.nodes()[v2_up]['position']
        x = (pos_v1[0] + pos_v2[0]) / 2
        y = (pos_v1[1] + pos_v2[1]) / 2
        pos_center = (x, y)

        # Check if they are connected
        if not graph.has_edge(v1_up, v2_up):
            raise ValueError('Upper vertices are not connected')

        # Prepare list of vertices in lower layer
        pairs_of_lower = [list(), list(), set()]
        for interior in prod_input[2:]:
            for v in get_neighbors_at(graph, interior, down_layer):
                if graph.nodes()[v]['position'] == pos_v1:
                    pairs_of_lower[0].append((v, lower_to_upper[interior]))
                elif graph.nodes()[v]['position'] == pos_v2:
                    pairs_of_lower[1].append((v, lower_to_upper[interior]))
                elif graph.nodes()[v]['position'] == pos_center:
                    if v not in pairs_of_lower[2]:
                        pairs_of_lower[2].add((v, lower_to_upper[interior]))

        # Check if sets have proper sizes
        if len(pairs_of_lower[0]) != 2:
            raise ValueError('Connections between lower vertices are incorrect')
        if len(pairs_of_lower[1]) != 2:
            raise ValueError('Connections between lower vertices are incorrect')
        if len(pairs_of_lower[2]) != 1:
            raise ValueError('Connections between lower vertices are incorrect')

        # Check if middle vertex is connected to two proper interiors
        middle = pairs_of_lower[2].pop()
        middle_side = middle[1]
        middle = middle[0]
        for interior in get_neighbors_at(graph, middle_side, down_layer):
            if not graph.has_edge(middle, interior):
                raise ValueError('Middle vertex is not connected to two proper interiors')

        # prepare vertexes to connect
        # And check if there is one common vertex between two sides
        single = None
        multiple = []
        # Confusing indexes pairs_of_lower[0][0][0] means:
        # pairs_of_lower[position - either 0 or 1][vertex in list][0 for vertex id]
        if pairs_of_lower[0][0][0] == pairs_of_lower[0][1][0]:
            single = pairs_of_lower[0][0][0]
            multiple = (pairs_of_lower[1][0][0], pairs_of_lower[1][1][0])
            multiple_side = (pairs_of_lower[1][0][1], pairs_of_lower[1][1][1])
        elif pairs_of_lower[1][0][0] == pairs_of_lower[1][1][0]:
            single = pairs_of_lower[1][0][0]
            multiple = (pairs_of_lower[0][0][0], pairs_of_lower[0][1][0])
            multiple_side = (pairs_of_lower[0][0][1], pairs_of_lower[0][1][1])
        else:
            raise ValueError('There is no connection between two sides')

        # Check if two vertices to merge are not the same
        if multiple[0] == multiple[1]:
            raise ValueError('Vertex to merge are one and the same')

        # Check if vertices to merge are not connected
        if graph.has_edge(multiple[0], multiple[1]):
            raise ValueError('Vertex to merge are connected')

        # Check if those vertices are properly connected
        if not graph.has_edge(single, middle):
            raise ValueError('Connections between lower vertices are incorrect')
        if middle_side == multiple_side[0]:
            if not graph.has_edge(single, multiple[1]):
                raise ValueError('Connections between lower vertices are incorrect')
            if not graph.has_edge(middle, multiple[0]):
                raise ValueError('Connections between lower vertices are incorrect')
        if middle_side == multiple_side[1]:
            if not graph.has_edge(single, multiple[0]):
                raise ValueError('Connections between lower vertices are incorrect')
            if not graph.has_edge(middle, multiple[1]):
                raise ValueError('Connections between lower vertices are incorrect')

        # Check if labels are E
        if any(graph.nodes()[v]['label'] != 'E' for v in [single, middle, multiple[0], multiple[1]]):
            raise ValueError('Not all vertices have label E')


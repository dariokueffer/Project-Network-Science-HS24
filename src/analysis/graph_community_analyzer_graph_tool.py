import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from graph_tool import Graph as graph_tool_graph
from graph_tool import generation
import matplotlib.cm
import graph_tool.all as gt


class GraphCommunityAnalyzerGraphTool:
    def __init__(self, graph: graph_tool_graph, output_filename: str):
        self.graph = graph
        self.output_filename = output_filename
        self.communities = {}
        self.randomized_graph = self.graph.copy()
        self.randomized_graph = generation.random_rewire(
            self.randomized_graph, n_iter=3)

        # self.randomized_graph = nx.algorithms.smallworld.random_reference(graph, niter=3, connectivity=False, seed=None)

    # def get_hierarchical_community_detection(self, is_random=False):
    #     gt.seed_rng(0)

    #     g = self.randomized_graph if is_random else self.graph
    #     print(f"Data type of graph: {type(g)}")
    #     sargs = dict(recs=[g.ep.weight], rec_types=["real-exponential"])
    #     state = gt.minimize_nested_blockmodel_dl(g, state_args=sargs)
    #     state.draw(edge_color=gt.prop_to_size(g.ep.weight, power=1,log=True),ecmap=(matplotlib.cm.inferno, .6),eorder=g.ep.weight,edge_pen_width=gt.prop_to_size(g.ep.weight,1, 4,power=1,log=True),edge_gradient=[])

    def calc_minimize_blockmodel_dl(self, is_random=False):
        suffix = "_random" if is_random else ""
        g = self.randomized_graph if is_random else self.graph
        state = gt.minimize_blockmodel_dl(g)
        self.communities[f'communities_modularity{suffix}'] = state.get_blocks()
        state.draw(vertex_shape=state.get_blocks(), output=f"{self.output_filename}_modularity{suffix}.png")

    # def calculate_community_quality(self, is_random=False):
    #     G = self.randomized_graph if is_random else self.graph
    #     suffix = "_random" if is_random else ""

    #     coomunities_greedy = self.communities[f'communities_greedy{suffix}']
    #     coomunities_label_prop = self.communities[f'communities_label_prop{suffix}']

    #     modularity_greedy = nx.community.quality.modularity(
    #         G, coomunities_greedy)
    #     modularity_label_prop = nx.community.quality.modularity(
    #         G, coomunities_label_prop)

    #     self.communities[f'modularity_greedy{suffix}'] = modularity_greedy
    #     self.communities[f'modularity_label_prop{suffix}'] = modularity_label_prop

    # def print_communities(self, is_comparison=False):
    #     print(50*'-')
    #     print(f"Graph: TBD")
    #     print()
    #     self.get_greedy_modularity_maximization_communities()
    #     self.calculate_community_quality()
    #     print(
    #         f"Number communities (label propagation algorithm): {len(self.communities['communities_label_prop'])}")
    #     print(
    #         f"Number communities (greedy modularity maximization algorithm): {len(self.communities['communities_greedy'])}")
    #     print()
    #     print(
    #         f"Modularity (Quality) (label propagation algorithm): {self.communities['modularity_label_prop']}")
    #     print(
    #         f"Modularity (Quality) (greedy modularity maximization algorithm): {self.communities['modularity_greedy']}")
    #     self.get_greedy_modularity_maximization_communities(True)
    #     self.calculate_community_quality(True)
    #     if is_comparison:
    #         print()
    #         print(
    #             f"Number communities (label propagation algorithm) - randomized graph: {len(self.communities['communities_label_prop_random'])}")
    #         print(
    #             f"Number communities (greedy modularity maximization algorithm) - randomized graph: {len(self.communities['communities_greedy_random'])}")
    #         print()
    #         print(
    #             f"Modularity (Quality) (label propagation algorithm) - randomized graph: {self.communities['modularity_label_prop_random']}")
    #         print(
    #             f"Modularity (Quality) (greedy modularity maximization algorithm) - randomized graph: {self.communities['modularity_greedy_random']}")

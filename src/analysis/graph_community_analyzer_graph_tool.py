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
        generation.random_rewire(self.randomized_graph, n_iter=3)
        print(f'Graph: {self.graph.num_vertices()} vertices, {self.graph.num_edges()} edges')
        print(f'Randomized Graph: {self.randomized_graph.num_vertices()} vertices, {self.randomized_graph.num_edges()} edges')


    def calc_minimize_blockmodel_dl(self, is_random=False, output_plot=False):
        suffix = "_random" if is_random else ""
        g = self.randomized_graph if is_random else self.graph
        state = gt.minimize_blockmodel_dl(g)
        self.communities[f'communities_blockmodel{suffix}'] = state.get_blocks()
        print(f"Number of blocks: {state.get_B()}")
        print(f"Effective number of blocks: {state.get_Be()}")
        print(f"Non-Empty number of blocks: {state.get_nonempty_B()}")

        if output_plot:
            state.draw(vertex_shape=state.get_blocks(), output=f"{self.output_filename}_blockmodel{suffix}.png")
    
    def calc_modularity_maximization(self, is_random=False, output_plot=False, niter=10):
        suffix = "_random" if is_random else ""
        g = self.randomized_graph if is_random else self.graph
        state = gt.ModularityState(g)
        state.mcmc_sweep(niter=niter)
        self.communities[f'communities_modularity{suffix}'] = state.b
        print(f"Number of blocks: {state.get_B()}")
        # print(f"Effective number of blocks: {state.get_Be()}") //bug in library
        if output_plot:
            state.draw(output=f"{self.output_filename}_modularity{suffix}.png")

    def calculate_modularity_newman(self, is_random=False, comm_type="blockmodel"):
            suffix = "_random" if is_random else ""
            g = self.randomized_graph if is_random else self.graph
            return gt.modularity(g, self.communities[f'communities_{comm_type}{suffix}'])

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

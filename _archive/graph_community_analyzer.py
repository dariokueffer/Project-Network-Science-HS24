import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

class GraphCommunityAnalyzer:
    def __init__(self, graph):
        self.graph = graph
        self.communities = {}
        self.randomized_graph = nx.algorithms.smallworld.random_reference(graph, niter=3, connectivity=False, seed=None)

    def get_greedy_modularity_maximization_communities(self, is_random=False):
        G = self.randomized_graph if is_random else self.graph

        suffix = "_random" if is_random else ""
        communities = nx.community.greedy_modularity_communities(G)
        temp_communities = []
        for comm in communities:
            temp_communities.append(list(comm))
        self.communities[f'communities_greedy{suffix}'] = temp_communities
        self.communities[f'communities_label_prop{suffix}'] = list(nx.community.label_propagation_communities(G))

    def calculate_community_quality(self, is_random=False):
        G = self.randomized_graph if is_random else self.graph
        suffix = "_random" if is_random else ""

        coomunities_greedy = self.communities[f'communities_greedy{suffix}']
        coomunities_label_prop = self.communities[f'communities_label_prop{suffix}']

        modularity_greedy = nx.community.quality.modularity(G, coomunities_greedy)
        modularity_label_prop = nx.community.quality.modularity(G, coomunities_label_prop)

        self.communities[f'modularity_greedy{suffix}'] = modularity_greedy
        self.communities[f'modularity_label_prop{suffix}'] = modularity_label_prop

    def print_communities(self, is_comparison=False):
        print(50*'-')
        print(f"Graph: TBD")
        print()
        self.get_greedy_modularity_maximization_communities()
        self.calculate_community_quality()
        print(f"Number communities (label propagation algorithm): {len(self.communities['communities_label_prop'])}")
        print(f"Number communities (greedy modularity maximization algorithm): {len(self.communities['communities_greedy'])}")
        print()
        print(f"Modularity (Quality) (label propagation algorithm): {self.communities['modularity_label_prop']}")
        print(f"Modularity (Quality) (greedy modularity maximization algorithm): {self.communities['modularity_greedy']}")
        self.get_greedy_modularity_maximization_communities(True)
        self.calculate_community_quality(True)
        if is_comparison:
            print()
            print(f"Number communities (label propagation algorithm) - randomized graph: {len(self.communities['communities_label_prop_random'])}")
            print(f"Number communities (greedy modularity maximization algorithm) - randomized graph: {len(self.communities['communities_greedy_random'])}")
            print()
            print(f"Modularity (Quality) (label propagation algorithm) - randomized graph: {self.communities['modularity_label_prop_random']}")
            print(f"Modularity (Quality) (greedy modularity maximization algorithm) - randomized graph: {self.communities['modularity_greedy_random']}")

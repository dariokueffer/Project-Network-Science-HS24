
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr, spearmanr, kendalltau
import math
from tqdm import tqdm
from graph_tool.correlations import scalar_assortativity
from graph_tool.generation import random_rewire
import graph_tool as gt
import numpy as np
import matplotlib.pyplot as plt
import multiprocessing
from graph_tool.centrality import closeness, betweenness, eigenvector
import time


class BasicGraphAnalyzer:
    def __init__(self, graph):
        self.graph = graph
        self.randomized_graph = None


    def get_degree_and_average_degree_of_neighbors(self, G=None):
        if G is None:
            G = self.graph

        degrees, average_degrees = [], []

        degree_map = G.degree_property_map("total")
        total_vertices = G.num_vertices()

        for v in tqdm(G.vertices(), total=total_vertices, desc="Processing vertices", unit="vertex"):
            neighbors = v.all_neighbors()

            sum_degrees = 0
            neighbor_count = 0

            for neighbor in neighbors:
                sum_degrees += degree_map[neighbor]
                neighbor_count += 1

            current_node_degree = degree_map[v]
            average_degree = sum_degrees / neighbor_count if neighbor_count > 0 else 0

            degrees.append(current_node_degree)
            average_degrees.append(average_degree)

        degree_dict = defaultdict(lambda: {'sum': 0, 'count': 0})

        for degree, avg_degree in zip(degrees, average_degrees):
            degree_dict[degree]['sum'] += avg_degree
            degree_dict[degree]['count'] += 1

        unique_degrees = []
        averaged_average_degrees = []

        for degree, values in degree_dict.items():
            unique_degrees.append(degree)
            averaged_average_degrees.append(values['sum'] / values['count'])

        return unique_degrees, averaged_average_degrees

    def plot_degree_vs_avg_degree(self, title, plot_randomized=False):
        x, y = self.get_degree_and_average_degree_of_neighbors()
        assortativity_real_network = self.calculate_assortativity()

        color = 'blue'
        label_real_network = f'Real network (assortativity: {assortativity_real_network:.3g})'
        data = [(x, y, color, label_real_network)]

        if plot_randomized:
            self.randomize_graph()

            x, y = self.get_degree_and_average_degree_of_neighbors(self.randomized_graph)
            assortativity_randomized_network = self.calculate_assortativity(self.randomized_graph)

            color = 'red'
            label_randomized_network = f'Randomized network (assortativity: {assortativity_randomized_network:.3g})'
            data.append((x, y, color, label_randomized_network))

        fig, ax = plt.subplots()
        for data_set in data:
            x, y, color, label = data_set
            ax.scatter(x, y, c=color, label=label, alpha=0.7)

        ax.legend()
        plt.xlabel('Degree')
        plt.ylabel('Average degree of neighbors')
        plt.title(title)
        plt.show()



    def calculate_assortativity(self, G=None):
        if G is None:
            G = self.graph

        degree_map = G.degree_property_map("total")
        assortativity, _ = scalar_assortativity(G, degree_map)
        return assortativity

    def plot_log_log_probability_density(self, title):
        G = self.graph
        
        degrees = G.get_total_degrees(G.get_vertices())
        
        logarithmic_bins = np.logspace(np.log10(max(1, min(degrees))), np.log10(max(degrees)), num=20)
        
        plt.hist(degrees, bins=logarithmic_bins, density=True)
        
        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel('Degree (k)')
        plt.ylabel('Probability Density p(k)')
        plt.title(title)
        plt.grid(True)
        plt.show()
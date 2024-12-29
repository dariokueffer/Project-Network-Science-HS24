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
from src.analysis.utils import randomize_graph
from graph_tool import openmp_set_num_threads


class CentralityAnalyzer:
    def __init__(self, graph):
        self.graph = graph
        self.randomized_graph = None
        self.measures = ['degrees','closeness', 'betweenness', 'eigenvector']
        self.centrality = {}


    def calculate_centralities(self, is_randomized=False, num_threads=4):
        # Enable parallel execution
        openmp_set_num_threads(num_threads)
        
        if is_randomized:
            G = randomize_graph(self.graph)
            suffix = '_randomized'
        else:
            G = self.graph
            suffix = ''
        
        try:
            print("Calculating degrees...")
            start_time = time.time()
            self.centrality[f'degrees{suffix}'] = G.get_total_degrees(G.get_vertices())
            print(f"Degrees calculated in {time.time() - start_time:.2f} seconds.\n")

            print("Calculating eigenvector...")
            start_time = time.time()
            eig = eigenvector(G, max_iter=100, epsilon=1e-6)
            self.centrality[f'eigenvector{suffix}'] = eig[1].get_array()
            print(f"Eigenvector centrality calculated in {time.time() - start_time:.2f} seconds.\n")


            print("Calculating closeness...")
            start_time = time.time()
            close = closeness(G)
            self.centrality[f'closeness{suffix}'] = close.get_array()
            print(f"Closeness centrality calculated in {time.time() - start_time:.2f} seconds.\n")


            print("Calculating betweenness...")
            start_time = time.time()
            vbet, _ = betweenness(G, norm=True)
            self.centrality[f'betweenness{suffix}'] = vbet.get_array()
            print(f"Betweenness centrality calculated in {time.time() - start_time:.2f} seconds.\n")

        
        except Exception as e:
            print(f"Error calculating centralities: {e}")
            raise
    

    def get_closeness_centrality(self, is_randomized=False):
        return self.centrality[f'closeness{"_randomized" if is_randomized else ""}']
    
    def get_betweenness_centrality(self, is_randomized=False):
        return self.centrality[f'betweenness{"_randomized" if is_randomized else ""}']
    
    def get_eigenvector_centrality(self, is_randomized=False):
        return self.centrality[f'eigenvector{"_randomized" if is_randomized else ""}']
    
    def get_degrees(self, is_randomized=False):
        return self.centrality[f'degrees{"_randomized" if is_randomized else ""}']
    
    
    def plot_log_log_centrality_distribution(self, centralities, logarithmic_bins, x_label='not defined', y_label='Probability Density'): 

        plt.hist(centralities, bins=logarithmic_bins, density=True)
        # plt.xscale('log')
        plt.yscale('log')
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title('Title')
        plt.show()

    def plot_centralities(self):
        self.calculate_centralities()

        for measure in self.measures:
            linear_bins = np.linspace(min(self.centrality[measure]), max(self.centrality[measure]), num=16)
            self.plot_log_log_centrality_distribution(self.centrality[measure], linear_bins, measure, 'TBD')


    def plot_centralities_comparison(self):

        self.calculate_centralities()

        measure_pairs = [(x, y) for x in self.measures for y in self.measures if x != y]
        for pair in measure_pairs:
            if (pair[1], pair[0]) in measure_pairs:
                measure_pairs.remove((pair[1], pair[0]))

        data_structure = []
        for measure_pair in measure_pairs:

            data_structure.append([(self.centrality[measure_pair[0]], self.centrality[measure_pair[1]], 'blue',
                                f"{measure_pair[0]} vs {measure_pair[1]}", measure_pair[0], measure_pair[1], 'Title')])

        self.plot_centrality_measure_vs_centrality_measure(
            data_structure, f"{measure_pair[0]} vs {measure_pair[1]}", show_legend=False)
    

  
    def plot_centrality_measure_vs_centrality_measure(self, data, overall_title, show_legend=True):
        n_plots = len(data)

        n_cols = min(3, math.ceil(math.sqrt(n_plots)))  
        n_rows = math.ceil(n_plots / n_cols)

        fig, ax = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 5 * n_rows))

        if n_rows == 1 and n_cols == 1:
            ax = [ax]
        else:
            ax = ax.flatten()

        for i in range(n_plots):
            corr_text = ""
            for data_point in data[i]:
                x, y, color, label, x_label, y_label, title = data_point
                pearson_corr, _ = pearsonr(x, y)
                spearman_corr, _ = spearmanr(x, y)
                kendall_corr, _ = kendalltau(x, y)
                corr_text += (
                    f"Pearson: {pearson_corr:.2f}\n"
                    f"Spearman: {spearman_corr:.2f}\n"
                    f"Kendall: {kendall_corr:.2f}"
                )
                ax[i].scatter(x, y, c=color, label=label, alpha=0.7)

            ax[i].text(0.05, 0.95, corr_text, transform=ax[i].transAxes,
                    fontsize=8, verticalalignment='top')
            if show_legend:
                ax[i].legend()
            ax[i].set_xlabel(x_label)
            ax[i].set_ylabel(y_label)
            ax[i].set_title(title)

        for j in range(n_plots, len(ax)):
            fig.delaxes(ax[j])

        fig.suptitle(overall_title, fontsize=16)
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.show()

    def plot_centralities_comparison_randomized(self):
        self.randomized_graph = randomize_graph(self.graph)
        self.calculate_centralities()
        self.calculate_centralities(True)


        measure_pairs_randomized = []
        for i in range(len(self.measures)):
            measure_pairs_randomized.append((self.measures[i], self.measures[i] + '_randomized'))
        data_structure = []

        for measure_pair in measure_pairs_randomized:
            data_structure.append([(self.centrality[measure_pair[0]], self.centrality[measure_pair[1]], 'blue',
                                    f"{measure_pair[0]} vs {measure_pair[1]}", measure_pair[0], measure_pair[1], 'Title')])
        self.plot_centrality_measure_vs_centrality_measure(
                data_structure, f"{measure_pair[0]} vs {measure_pair[1]}", show_legend=False)
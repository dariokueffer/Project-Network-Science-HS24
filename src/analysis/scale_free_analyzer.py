import powerlaw
import numpy as np
import matplotlib.pyplot as plt
from scipy import special


class ScaleFreeAnalyzer():
    def __init__(self, G, is_weighted=False):
        self.G = G
        self.is_weighted = is_weighted

    def calculate_poisson_degree_distribution(self, degrees, logarithmic_bins):
        lamda = np.mean(degrees)
        x = logarithmic_bins
        y = np.exp(-lamda) * np.power(lamda, x) / special.factorial(x)
        x = x[y > 0]
        y = y[y > 0]
        return x, y

    def calculate_exponential_degree_distribution(self, degrees, logarithmic_bins):
        lamda = np.mean(degrees)
        beta = 1 / lamda
        x = logarithmic_bins
        y = beta * np.exp(-beta * x)
        # remove entries with 0 probability
        x = x[y > 0]
        y = y[y > 0]
        return x, y


    def get_degrees(self, G, weighted=False):
        if weighted:
            weights = G.edge_properties["weight"]
            return [sum(weights[e] for e in v.out_edges()) for v in G.vertices()]
        else:
            return G.get_out_degrees(G.get_vertices())

    def fit_power_law(self, degrees):
        fit = powerlaw.Fit(degrees)
        return fit.power_law.alpha, fit.power_law.sigma

        
    def calculate_power_law_degree_distributio(self):
        print(50*'-')
        degrees = self.get_degrees(self.G, weighted=self.is_weighted)
        alpha, sigma = self.fit_power_law(degrees)
        print()
        print()
        print(f'Exponent: {alpha}')
        print(f'Error: {sigma}')

    def plot_degree_distribution(self, graph, title):
        degrees = self.get_degrees(graph, self.is_weighted)
        title = f"Graph: {title}"
        print(f"{20*'-'} {title} {20*'-'}")
        # print(f"Number of Nodes: {len(graph['graph'])}")
        print(f"Graph average degree: {np.mean(degrees)}")
        print(f"Graph max degree: {max(degrees)}")
        print(f"Graph min degree: {min(degrees)}")
        print((42 + len(title))*'-')

        logarithmic_bins = np.logspace(np.log10(min(degrees)), np.log10(max(degrees)), num=20)

        # plot histogram as line and dots
        hist_densitiy, bin_edges = np.histogram(degrees, bins=logarithmic_bins, density=True)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2  # Find the center of each bin
        #remove values with 0 probability
        bin_centers = bin_centers[hist_densitiy > 0]
        hist_densitiy = hist_densitiy[hist_densitiy > 0]
        plt.plot(bin_centers, hist_densitiy, '-o', label='Degree', alpha=0.8)

        x,y = self.calculate_poisson_degree_distribution(degrees, logarithmic_bins)
        plt.plot(x, y, color='g', linestyle='-', label='Poisson Distribution')

        x,y = self.calculate_exponential_degree_distribution(degrees, logarithmic_bins)
        plt.plot(x, y, color='b', linestyle='-', label='Exponential Distribution')

        # add the power law fit to the plot
        fit = powerlaw.Fit(degrees, discrete=True, xmin=1)
        fit.power_law.plot_pdf(color='r', linestyle='--', label='Power Law Fit')

        plt.xscale('log')  # This was missing in original
        plt.yscale('log')
        plt.ylim([0.001*min(hist_densitiy), 100*max(hist_densitiy)])
        plt.legend()
        plt.title(f'Degree Distribution {title}')
        plt.xlabel('Degree')
        plt.ylabel('Probability Density')
        plt.show()
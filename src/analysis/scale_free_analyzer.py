import powerlaw
import numpy as np
import matplotlib.pyplot as plt
from scipy import special


class ScaleFreeAnalyzer():
    def __init__(self, G, is_weighted=False):
        self.G = G
        self.is_weighted = is_weighted
        self.is_filtered = False
        self.filter = None

    def set_filter(self, filter):
        self.is_filtered = True
        self.filter = filter

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


    def get_degrees(self, weighted=False):
        if weighted:
            weights = self.G.edge_properties["weight"]
            return [sum(weights[e] for e in v.out_edges()) for v in self.G.vertices()]
        else:
            return self.G.get_out_degrees(self.G.get_vertices())

    def fit_power_law(self, degrees):
        fit = powerlaw.Fit(degrees)
        return fit.power_law.alpha, fit.power_law.sigma

    def calculate_power_law_degree_distribution(self):
            print(50*'-')
            degrees = self.get_degrees(weighted=self.is_weighted)
            if self.is_filtered:
                filtered_degrees = [d for d in degrees if d > self.filter]
                alpha, sigma = self.fit_power_law(filtered_degrees)
            else:
                alpha, sigma = self.fit_power_law(degrees)
            print()
            print()
            print(f'Exponent: {alpha:.3f}')
            print(f'Error: {sigma:.3f}')
            return alpha, sigma

    def plot_degree_distribution(self, title):
        degrees = self.get_degrees(weighted=self.is_weighted)
        title = f"Graph: {title}"
        
        logarithmic_bins = np.logspace(np.log10(max(1, min(degrees))), 
                                    np.log10(max(degrees)), 
                                    num=20)
        
        hist_density, bin_edges = np.histogram(degrees, bins=logarithmic_bins, density=True)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        mask = hist_density > 0
        bin_centers = bin_centers[mask]
        hist_density = hist_density[mask]
        
        plt.figure(figsize=(10, 6))
        plt.plot(bin_centers, hist_density, '-o', label='Degree', alpha=0.8)
        
        x, y = self.calculate_poisson_degree_distribution(degrees, logarithmic_bins)
        plt.plot(x, y, color='g', linestyle='-', label='Poisson Distribution')
        
        x, y = self.calculate_exponential_degree_distribution(degrees, logarithmic_bins)
        plt.plot(x, y, color='b', linestyle='-', label='Exponential Distribution')
        
        degrees_array = np.array(degrees)
        xmin = 1
        if self.is_filtered:
            xmin = self.filter
            filtered_degrees = degrees_array[degrees_array >= self.filter]
        else:
            filtered_degrees = degrees_array
        
        if len(filtered_degrees) > 0:
            fit = powerlaw.Fit(filtered_degrees, discrete=True, xmin=xmin)
            fit.power_law.plot_pdf(color='r', linestyle='--', 
                                label=f'Power Law Fit (α={fit.alpha:.2f})')
        
        plt.xscale('log')
        plt.yscale('log')
        plt.ylim([0.001*min(hist_density), 100*max(hist_density)])
        plt.legend()
        plt.title(f'Degree Distribution {title}')
        plt.xlabel('Degree')
        plt.ylabel('Probability Density')
        plt.tight_layout()
        plt.show()
        
        print(f"\nPower Law Analysis:")
        print(f"Minimum degree considered (xmin): {xmin}")
        print(f"Number of nodes in tail: {len(filtered_degrees)}")
        print(f"Power law exponent (α): {fit.alpha:.3f} ± {fit.sigma:.3f}")
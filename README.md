# Network Science Project

The original Jupyter notebook crawling the Wikipedia pages can be found at [notebookes/wiki-data-acquisition.ipynb](notebookes/wiki-data-acquisition.ipynb). I started refactoring the code, removing certain parts from the notebook and putting them in separate files. The generated graphs and the database file can be found here in this [Dropbox](https://www.dropbox.com/scl/fo/g6qklql2q2s53qvp6y3n1/ACHF47mTMe5uUL759gj7CGI?rlkey=zhibh8nhejatt6lbwgd1hlp9u&st=9p1ooacn&dl=0). The database file needs to be placed in [src/acquisition/models/db](src/acquisition/models/db) and the graph files in [outputs/graphs](outputs/graphs).

## Requirements

To improve performance, we use graph-tool instead of networkx. In graph-tool the core algorithms and data structures are implemented in C++. To install graph-tool, follow the instructions below:

You can install graph-tool using Conda or directly with system packages and pip.

**Using Conda**

If you are using Conda, you can install graph-tool from the conda-forge channel:

````
conda install -c conda-forge graph-tool
````

Make sure that the conda-forge channel is enabled in your environment.

**Plain Installation (System Packages + pip)**

For a plain installation, you need to ensure that your system has the required dependencies before installing graph-tool.

***On Debian/Ubuntu:***

```
sudo apt-get update
sudo apt-get install -y build-essential libboost-all-dev libcgal-dev python3-pip python3-dev
pip install graph-tool
```

***On macOS (using Homebrew):***

````
brew install boost cgal
pip install graph-tool
````

For other systems, consult the official [graph-tool documentation](https://graph-tool.skewed.de/installation.html) for required dependencies.

 **Install the remaining Python dependencies:**

 ````
 pip install -r requirements.txt
````
## Running the Code

There are two main Jupyter notebooks, one for [data acquisition](acquisition.ipynb) and one for [data analysis](analysis.ipynb). Both use code that is implemented in other files, which are also structured according to [acquisition](src/acquisition/) and [analysis](src/analysis/).

## Data Acquisition

### Contributor Graph Builder

The ContributorGraphBuilder class implemented in [src/acquisition/graph-tool/contributor_graph_builder.py](src/acquisition/graph-tool/contributor_graph_builder.py) creates a networkx graph based on the crawled data.

## Data Analysis

### GraphAnalyzer

The GraphAnalyzer class implemented in [src/analysis/basic_graph_analyzer.py](src/analysis/basic_graph_analyzer.py) provides some tools for basic graph analysis.The following features are currently implemented: 

- Plot Degree vs. Average Degree of neighbors
- Log-log plot of probability density
- Plot centralities: degree, betweenness, closeness, eigenvector
- Plot comparison of different centralities
- Plot comparison of real to randomized network for all centralities


### CentralityAnalyzer

Implemented at [src/analysis/centrality_analyzer.py](src/analysis/centrality_analyzer.py)

// TBD

### Scale-free Analyzer

Currently still in the notebook [analysis.py](analysis.ipynb)

// TBD

## GraphCommunityAnalyzer

The GraphCommunityAnalyzer class implemented in [src/analysis/graph_community_analyzer.py](src/analysis/graph_community_analyzer.py) provides some tools for basic community analysis. The following features are currently implemented: 

- Community detection with reedy modularity maximization
- Community detection with label propagation algorithm
- Comparison to randomized networks

## Implementation

### Database

The file [src/models/models.py](src/models/models.py) contains the models for the database entities. The following figure shows the relationships.

![Database Relations](outputs/image.png)


## Crawled Categories

The table below shows the main categories crawled and some key metrics for each main category. The following graphs show the evolution of some of these metrics over time for each category.

| Category                | Number of Subcategories | Number of Pages | Number of Contributors | Number of Revisions |
| ----------------------- | ----------------------- | --------------- | ---------------------- | ------------------- |
| Amiga CD32 games        | 2                       | 143             | 8013                   | 29370               |
| Game boy games          | 6                       | 167             | 8953                   | 30851               |
| Machine learning        | 61                      | 1548            | 75217                  | 273260              |
| Artificial intelligence | 109                     | 8695            | 610800                 | 29368               |

***Amiga CD32 games***

![Amiga CD32 games](outputs/Amiga_CD32_games.png)

***Game boy games***

![Game boy games](outputs/Game_boy_games.png)

***Machine learning***

![Machine learning](outputs/Machine_learning.png)

***Artificial intelligence***

![Artificial intelligence](outputs/Artificial_intelligence.png)
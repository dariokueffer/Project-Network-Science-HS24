import networkx as nx
from tqdm import tqdm
import pickle

class ContributorGraphBuilder:
    def __ini__(self, db_manager, main_category_id=1):
        self.db_manager = db_manager
        self.main_category_id = main_category_id
        self.graph = nx.Graph()

    def fetch_contributors(self):
        contributors = db_manager.get_all_contributors(main_category_id=main_category_id)
        print(f"Total contributors: {len(all_contributors)}")
        return contributors

    def add_nodes(self, contributors):
        for contributor in contributors:
            # self.graph.add_node(contributor.id, username=contributor.username)
            self.graph.add_node(contributor.id)

    def add_edges(self, contributors):
        with tqdm(total=len(contributors), desc="Adding edges", unit="contributor") as pbar:
            for contributor in contributors:
                co_contributors = db_manager.get_co_contributors(contributor.id)
                for co_contributor_id in co_contributors:
                    if not G.has_edge(contributor.id, co_contributor_id):
                        G.add_edge(contributor.id, co_contributor_id)
                pbar.update(1)
    
    def build(self):
        contributors = self.fetch_contributors()
        self.add_nodes(contributors)
        self.add_edges(contributors)
        return self.graph

    def save_as_gml(self, name):
        nx.write_gml(G, f"{name}.gml")
        print(f"Graph saved as {name}.gml")

    def save_as_gpicke(self, name):
        with open(f"{name}.gpickle", "wb") as f:
            pickle.dump(G, f)
        print(f"Graph saved as {name}.gpickle")

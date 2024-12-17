import networkx as nx
from tqdm import tqdm
import pickle
from graph_tool.all import Graph

class ContributorGraphBuilder:
    def __init__(self, db_manager, name, weighted=False):
        self.db_manager = db_manager
        self.main_category_id = db_manager.get_main_category_by_name(name)
        self.graph = Graph(directed=False)

        self.node_ids = self.graph.new_vertex_property("int")
        self.graph.vertex_properties["id"] = self.node_ids

        self.name = name

        self.weighted = weighted
        if weighted:
            self.edge_weights = self.graph.new_edge_property("int")
            self.graph.edge_properties["weight"] = self.edge_weights

    def fetch_contributors(self):
        contributors = self.db_manager.get_all_contributors(main_category_id=self.main_category_id)
        print(f"Total contributors: {len(contributors)}")
        return contributors

    def add_nodes(self, contributors):
        for contributor in contributors:
            v = self.graph.add_vertex()
            self.node_ids[v] = contributor.id 

    def add_edges(self, contributors):
        total = len(contributors)
        total_edges_added = 0
        max_edges_for_one = 0
        contributor_with_most = None
        
        # Create a lookup dictionary for faster vertex finding
        vertex_lookup = {}
        for v in self.graph.vertices():
            vertex_lookup[self.node_ids[v]] = v
        
        with tqdm(total=total, desc="Adding edges", unit=" contributors") as pbar:
            for contributor in contributors:
                try:
                    if self.weighted:
                        co_contributors = self.db_manager.get_co_contributors_weighted(
                            contributor.id, 
                            self.main_category_id
                        )
                    else:
                        co_contributors = self.db_manager.get_co_contributors(
                            contributor.id, 
                            self.main_category_id
                        )
                        
                    edges_added_this_contributor = 0
                    contributor_vertex = vertex_lookup[contributor.id]
                    
                    # Batch process co-contributors
                    if self.weighted:
                        for co_contributor_id, weight in co_contributors.items():
                            if co_contributor_id in vertex_lookup:
                                co_contributor_vertex = vertex_lookup[co_contributor_id]
                                edge = self.graph.edge(contributor_vertex, co_contributor_vertex)
                                
                                if not edge:
                                    edge = self.graph.add_edge(contributor_vertex, co_contributor_vertex)
                                    self.edge_weights[edge] = weight
                                    edges_added_this_contributor += 1
                                    total_edges_added += 1
                                else:
                                    # Update weight if new weight is higher
                                    self.edge_weights[edge] = max(self.edge_weights[edge], weight)
                    else:
                        for co_contributor_id in co_contributors:
                            if co_contributor_id in vertex_lookup:
                                co_contributor_vertex = vertex_lookup[co_contributor_id]
                                if not self.graph.edge(contributor_vertex, co_contributor_vertex):
                                    self.graph.add_edge(contributor_vertex, co_contributor_vertex)
                                    edges_added_this_contributor += 1
                                    total_edges_added += 1
                    
                    if edges_added_this_contributor > max_edges_for_one:
                        max_edges_for_one = edges_added_this_contributor
                        contributor_with_most = contributor.id
                    
                    pbar.update(1)
                    
                except Exception as e:
                    print(f"\nError processing contributor {contributor.id}: {str(e)}")
                    continue
        
        print(f"\nDetailed Edge Statistics:")
        print(f"Total edges added: {total_edges_added}")
        print(f"Maximum edges for one contributor: {max_edges_for_one} (Contributor ID: {contributor_with_most})")
        print(f"Average edges per contributor: {total_edges_added/total:.2f}")
    
    def build(self):
        contributors = self.fetch_contributors()
        self.add_nodes(contributors)
        self.add_edges(contributors)

        # Print sanity check statistics
        num_vertices = self.graph.num_vertices()
        num_edges = self.graph.num_edges()
        print(f"\nGraph Statistics:")
        print(f"Number of vertices (contributors): {num_vertices}")
        print(f"Number of edges (collaborations): {num_edges}")
        
        file_name = self.name.replace(" ", "_")
        self.save_as_gt(file_name)
        
    def save_as_gt(self, name):
        weighted_suffix = "-weighted" if self.weighted else ""
        self.graph.save(f"outputs/graphs/{name}{weighted_suffix}.gt", fmt="gt")
        print(f"Graph saved as {name}{weighted_suffix}.gt")

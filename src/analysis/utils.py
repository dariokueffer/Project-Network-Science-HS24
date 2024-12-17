def randomize_graph(G):
    randomized_graph = G.copy()
    random_rewire(randomized_graph, 
            model="configuration",
            n_iter=3)
    return randomized_graph
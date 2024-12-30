from graph_tool.generation import random_rewire
import matplotlib.pyplot as plt

def randomize_graph(G):
    randomized_graph = G.copy()
    random_rewire(randomized_graph, 
            model="configuration",
            n_iter=3)
    return randomized_graph

def get_node_ids_from_community(G, communities, target_community_id):
    nodes_in_community = [v for v in G.vertices() if communities[v] == target_community_id]
    return nodes_in_community

def plot_stats_for_category_quarterly(df, category_name):
    # Add a 'quarter' column based on the 'month'
    df['quarter'] = df['month'].dt.to_period('Q')

    # Aggregate data by quarter (only numeric columns)
    quarterly_df = (
        df.groupby('quarter')[['total_contributions', 'unique_pages', 'unique_contributors']]
        .sum()
        .reset_index()
    )

    # Convert the 'quarter' back to a string for plotting
    quarterly_df['quarter'] = quarterly_df['quarter'].astype(str)

    # Plot the data
    plt.figure(figsize=(10, 6))
    plt.plot(quarterly_df['quarter'], quarterly_df['unique_pages'], label='Unique Pages')
    plt.plot(quarterly_df['quarter'], quarterly_df['unique_contributors'], label='Unique Contributors')
    plt.plot(quarterly_df['quarter'], quarterly_df['total_contributions'], label='Total Contributions')
    plt.title(f'Quarterly Statistics for Main Category: {category_name}')
    plt.xlabel('Quarter')
    plt.ylabel('Count')
    plt.legend()
    plt.grid(True)

    # Customize x-axis ticks: Show every 5th year
    xticks = quarterly_df['quarter'][::20]  # Adjust the interval as needed
    plt.xticks(ticks=range(0, len(quarterly_df['quarter']), 20), labels=xticks, rotation=45)

    plt.tight_layout()
    plt.show()
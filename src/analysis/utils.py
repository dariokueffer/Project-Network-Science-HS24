from graph_tool.generation import random_rewire
import matplotlib.pyplot as plt
import pandas as pd

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

    quarterly_df = (
        df.groupby('quarter')[['total_contributions', 'unique_pages', 'unique_contributors']]
        .sum()
        .reset_index()
    )

    # Convert the 'quarter' back to a string for plotting
    quarterly_df['quarter'] = quarterly_df['quarter'].astype(str)

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
    xticks = quarterly_df['quarter'][::20]
    plt.xticks(ticks=range(0, len(quarterly_df['quarter']), 20), labels=xticks, rotation=45)

    plt.tight_layout()
    plt.show()

def plot_stats_for_category_quarterly(df, category_name):
        if not pd.api.types.is_datetime64_any_dtype(df['month']):
                df['month'] = pd.to_datetime(df['month'])

        df['quarter'] = df['month'].dt.to_period('Q')

        min_quarter = df['quarter'].min()
        max_quarter = df['quarter'].max()
        all_quarters = pd.period_range(start=min_quarter, end=max_quarter, freq='Q')

        complete_quarters_df = pd.DataFrame(index=all_quarters)
        complete_quarters_df.index.name = 'quarter'

        quarterly_df = (
                df.groupby('quarter')[['total_contributions', 'unique_pages', 'unique_contributors']]
                .sum()
        )

        quarterly_df = (
                complete_quarters_df
                .join(quarterly_df)
                .fillna(0)
                .reset_index()
        )

        quarterly_df['quarter'] = quarterly_df['quarter'].astype(str)

        plt.figure(figsize=(10, 6))
        plt.plot(quarterly_df['quarter'], quarterly_df['unique_pages'], 
                label='Unique Pages')
        plt.plot(quarterly_df['quarter'], quarterly_df['unique_contributors'], 
                label='Unique Contributors')
        plt.plot(quarterly_df['quarter'], quarterly_df['total_contributions'], 
                label='Total Contributions')

        plt.title(f'Quarterly Statistics for Main Category: {category_name}')
        plt.xlabel('Quarter')
        plt.ylabel('Count')
        plt.legend()
        plt.grid(True)

        xticks = quarterly_df['quarter'][::20]  
        plt.xticks(ticks=range(0, len(quarterly_df['quarter']), 20), 
                labels=xticks, rotation=45)

        plt.tight_layout()
        plt.show()
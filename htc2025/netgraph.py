import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx

# Apply Seaborn theme
sns.set_theme(style="white")

# Create a mock graph
G = nx.Graph()

# Add nodes and edges
nodes = ['A', 'B', 'C', 'D', 'E']
edges = [('A', 'B'), ('A', 'C'), ('B', 'D'), ('C', 'D'), ('D', 'E')]

G.add_nodes_from(nodes)
G.add_edges_from(edges)

# Create positions for nodes
pos = nx.spring_layout(G, seed=42)  # spring layout for aesthetics

# Draw the graph
plt.figure(figsize=(8, 6))
nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=1000, edgecolors='k')
nx.draw_networkx_edges(G, pos, width=2, alpha=0.6)
nx.draw_networkx_labels(G, pos, font_size=14, font_weight='bold')

# Title and styling
plt.title("Mock Network Graph", size=16, weight='bold', pad=20)
plt.axis('off')
plt.tight_layout()
#plt.show()
plt.savefig("networkgraph.png")


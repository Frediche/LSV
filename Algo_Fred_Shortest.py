import random
from pysat.solvers import Glucose3

def generate_connected_graph(num_nodes):
    """Generate a connected graph as an adjacency list."""
    graph = {i: set() for i in range(num_nodes)}
    edges = []

    # Ensure the graph is connected by creating a spanning tree
    nodes = list(range(num_nodes))
    random.shuffle(nodes)
    for i in range(num_nodes - 1):
        u, v = nodes[i], nodes[i + 1]
        graph[u].add(v)
        graph[v].add(u)
        edges.append((u, v))

    # Add additional random edges
    for _ in range(num_nodes):  # Adding a few random edges
        u, v = random.sample(range(num_nodes), 2)
        if v not in graph[u]:
            graph[u].add(v)
            graph[v].add(u)
            edges.append((u, v))

    return graph, edges


def encode_cnf(graph, source, target, path_length, num_nodes):
    """Encode the shortest path problem into CNF with a given path length."""
    clauses = []
    # Variables: x_i_j = node i is in position j in the path
    var = lambda i, j: i * path_length + j + 1

    # Each position in the path must have exactly one node
    for j in range(path_length):
        clauses.append([var(i, j) for i in range(num_nodes)])  # At least one
        for i in range(num_nodes):
            for k in range(i + 1, num_nodes):
                clauses.append([-var(i, j), -var(k, j)])  # At most one

    # Each node must appear at most once in the path
    for i in range(num_nodes):
        for j in range(path_length):
            for k in range(j + 1, path_length):
                clauses.append([-var(i, j), -var(i, k)])

    # Add constraints for edges (only connected nodes can follow each other)
    for j in range(path_length - 1):
        for i in range(num_nodes):
            for k in range(num_nodes):
                if k not in graph[i]:
                    clauses.append([-var(i, j), -var(k, j + 1)])

    # Source must be the first node and target the last
    clauses.append([var(source, 0)])
    clauses.append([var(target, path_length - 1)])

    return clauses

def solve_shortest_path(graph, source, target, num_nodes):
    """Iteratively solve for the shortest path."""
    for path_length in range(2, num_nodes + 1):
        clauses = encode_cnf(graph, source, target, path_length, num_nodes)
        solver = Glucose3()
        for clause in clauses:
            solver.add_clause(clause)

        if solver.solve():
            model = solver.get_model()
            path = [-1] * path_length
            for i in range(num_nodes):
                for j in range(path_length):
                    if model[(i * path_length) + j] > 0:
                        path[j] = i
            return path
    return None

def print_graph(graph):
    """Print a visual representation of the graph."""
    print("\nGraph:")
    for node, neighbors in graph.items():
        print(f"Node {node}: Connected to {sorted(neighbors)}")

# Main Execution
num_nodes = 30
graph, edges = generate_connected_graph(num_nodes)
print_graph(graph)

source, target = random.sample(range(num_nodes), 2)
print(f"\nSource: {source}, Target: {target}")

path = solve_shortest_path(graph, source, target, num_nodes)

if path:
    print("\nShortest Path found:")
    print(" -> ".join(map(str, path)))
else:
    print("\nNo path found.")


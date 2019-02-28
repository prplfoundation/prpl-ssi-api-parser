

class Graph:
    """Graph groups multiple nodes into a Graphviz cluster/graph."""

    def __init__(self):
        """Initializes the Graph object."""

        self.nodes = {}

    def append(self, node):
        """Adds the provided node/tree to the cluster.

        Args:
            node (Node): Node/tree to be added to the cluster as root node.

        """

        self.nodes[node.name] = node

    def dot(self, indent_interval=2):
        """Converts the graph to a Graphviz graph.

        Args:
            indent_interval (int): Number of spaces used for identation.

        Returns:
            str: Graphviz graph.

        """

        indentation = ' ' * indent_interval

        nodes = map(lambda x: '{}\n'.format(x.dot(indent_interval)), self.nodes.values())
        nodes = ''.join(nodes)

        dot = 'graph G {\n'
        dot += indentation + 'graph [font="Calibri Light" fontsize=11 style=dashed penwidth=0.5]\n'
        dot += indentation + 'node [shape=box font="Calibri Light" fontsize=11 style=dashed penwidth=0.5]\n'
        dot += nodes
        dot += '}'

        return dot

    def __str__(self):
        """Formats the node cluster as a string.

        Returns:
            str: Human-friendly textual representation of the sub-tree.

        """

        nodes = list(map(lambda x: str(x), self.nodes.values()))
        return ''.join(nodes)[:-1]

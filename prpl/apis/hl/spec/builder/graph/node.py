
class Node:
    """Node is the main TreeNode construct for generating a Tree graph."""

    def __init__(self, index, name, parent=None):
        """Initializes the Node object.

        Args:
            index (str): Unique id of node.
            name (str): Name of the node.
            parent (Node): Parent node.

        """

        self.index = index
        self.name = name
        self.nodes = {}
        self.parent = parent

    def append(self, node):
        """Appends a new node as a child.

        Args:
            node (Node): Child node.

        """

        node.parent = self
        self.nodes[node.name] = node

    def depth(self):
        """Traverses the tree back to its root node and calculates the node depth.

        Returns:
            int: Depth of the node.
        """

        if self.parent is None:
            return 0
        else:
            return 1 + self.parent.depth()

    def is_leaf(self):
        """Validates whether the node is a leaf (terminal) node.

        Returns:
            bool: True if the node has no child nodes, False otherwise.

        """

        if len(self.nodes) == 0:
            return True
        else:
            return False

    def dot(self, indent_interval=2):
        """Converts the sub-tree to a Graphviz cluster.

        Args:
            indent_interval (int): Number of spaces used for indentation.

        Returns:
            str: Graphviz graph.

        """

        indentation = indent_interval * ' ' + indent_interval * ' ' * self.depth()

        if self.is_leaf():
            return '{}node [label="{}"] {}'.format(indentation, self.name, self.index)
        else:
            children = map(lambda x: '{}\n'.format(x.dot(indent_interval)), self.nodes.values())
            children = ''.join(children)

            dot = indentation + 'subgraph cluster' + str(self.index) + ' {\n'
            dot += indentation + ' ' * indent_interval + 'label="' + self.name + '"\n'
            dot += children
            dot += indentation + '}'

            return dot

    def __str__(self):
        """Formats the sub-tree as a string.

        Returns:
            str: Human-friendly textual representation of the sub-tree.

        """

        indent_space = 2

        if self.is_leaf():
            symbol = '-'
        else:
            symbol = '+'

        node = '{}{} {}\n'.format(indent_space * ' ' * self.depth(), symbol, self.name)

        children = list(map(lambda x: str(x), self.nodes.values()))
        return node + ''.join(children)

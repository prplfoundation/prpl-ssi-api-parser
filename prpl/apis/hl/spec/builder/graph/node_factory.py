
from prpl.apis.hl.spec.builder.graph.graph import Graph
from prpl.apis.hl.spec.builder.graph.node import Node


class NodeFactory:
    """NodeFactory converts Converts Generates a raphviz open source graph visualization software writer for prpl HL-API.

        Congenerates a visual representation of the specification using.
    """

    index = -1

    @staticmethod
    def get_node(name, parent=None):
        """Generates a new tree node with a unique index.

        Args:
            name (str): Node name of node to be created.
            parent (Node): Parent node of the node to be created.

        Returns:
            Node: New node.

        """

        NodeFactory.index += 1
        return Node(NodeFactory.index, name, parent)

    @staticmethod
    def get_graph(objects):
        """Parses a list of objects and builds a cluster of trees.

        Args:
            objects (list<str>): List of object strings to be converted into nodes.

        Returns:
            Graph: Cluster of tree nodes.

        """

        d = Graph()

        for o in objects:
            tokens = o.split('.')

            n = d
            for t in tokens:
                try:
                    n = n.nodes[t]
                except KeyError:
                    if n == d:
                        parent = None
                    else:
                        parent = n

                    n.append(NodeFactory.get_node(t, parent))
                    n = n.nodes[t]

        return d

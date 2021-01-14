import graphviz as g
import nodes
from typing import List

class Visualizer:

    def __init__(self, root : nodes.Root, file_name: str) -> None:
        self.root = root
        self.file_name = file_name
        self.id = 0
        self.graph = g.Digraph(f"Visualizing of {file_name}")

    def visualize(self):
        self.create_subtree(self.root)
        self.graph.render('output/output')
    
    def create_subtree(self, node: nodes.Node) -> str:
        key = str(self.id)
        value = node.value if hasattr(node, 'value')  else node.children.__str__()
        self.graph.node(key, f'{node.__class__.__name__}\n {value}')
        self.id += 1
        if hasattr(node, 'children'):
            for child in node.children:
                child_key = self.create_subtree(child)
                self.graph.edge(key, child_key)
        return key


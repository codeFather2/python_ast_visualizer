from io import TextIOWrapper
import graphviz as g
import nodes
from typing import List, Tuple
from enum import Enum
from lexer_utils import TokenType

class VisualizingMode(Enum):
    AST = 0
    EXECUTION = 1

class Visualizer:

    def __init__(self, root : nodes.Root, file_name: str, source_code : str) -> None:
        self.root = root
        self.file_name = file_name
        self.id = 0
        self.graph = g.Digraph(f"Visualizing of {file_name}")
        self.source_code = source_code

    def visualize(self, mode : VisualizingMode):
        self.id = 0
        self.graph = g.Digraph(f"Visualizing of {self.file_name}")

        if mode == VisualizingMode.AST:
            self.visualize_ast('Root', self.root)
        elif mode == VisualizingMode.EXECUTION:
            self.visualize_execution('Entry', self.root)
        self.graph.render(f'output/output{mode}')
    
    def visualize_ast(self, node_name: str, node: nodes.Node) ->  str:
        key = str(self.id)
        node_name = node_name.capitalize() if len(node_name) > 0 else node.__class__.__name__
        self.graph.node(key, f'{node_name}\n\n{self.get_text_for_node(node)}')
        self.id += 1
        fields_to_exclude = ['children', 'value', 'span']
        children = list(filter(lambda x: x[0] not in fields_to_exclude, node.__dict__.items()))
        
        if len(children) == 0 and hasattr(node, 'children'):
            for child in node.children:
                child_key = self.visualize_ast('', child)
                self.graph.edge(key, child_key)
        else:
            for name, child in children:
                if child is None:
                    continue
                child_key = self.visualize_ast(name, child)
                self.graph.edge(key, child_key)
        return key

    def visualize_execution(self, node_name: str, node: nodes.Node) ->  str:
        key = str(self.id)
        node_name = node_name.capitalize() if len(node_name) > 0 else node.__class__.__name__
        self.graph.node(key, f'{node_name}\n\n{self.get_text_for_node(node)}')
        self.id += 1
        fields_to_exclude = ['children', 'value', 'span']
        children = list(filter(lambda x: x[0] not in fields_to_exclude, node.__dict__.items()))
        child_keys: List[str] = []
        if len(children) == 0 and hasattr(node, 'children'):
            for child in node.children:
                child_keys.append(self.visualize_execution('', child))
        else:
            for name, child in children:
                if child is None:
                    continue
                child_keys.append(self.visualize_execution(name, child))

        if len(child_keys) > 0:
            self.graph.edge(key, child_keys[0])
            for index in range(1, len(child_keys)):
                current = child_keys[index]
                prev = child_keys[index - 1]
                self.graph.edge(prev, current)
        return key

    def get_text_for_node(self, node: nodes.Node) -> str:
        if isinstance(node, TokenType):
            return str(node)
        if isinstance(node, nodes.Root):
            return ''
        if issubclass(type(node), nodes.Terminal):
            return node.value
        else:
            return self.source_code[node.span.begin: node.span.end]
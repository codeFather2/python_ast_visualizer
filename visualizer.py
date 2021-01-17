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

    def __init__(self, root : nodes.Root, file_name: str, source_code : str, output_file : str) -> None:
        self.root = root
        self.file_name = file_name
        self.output = output_file if output_file and len(output_file) > 0 else 'output/output'
        self.id = 0
        self.graph = g.Digraph(f"Visualizing of {file_name}")
        self.source_code = source_code
        self.fields_to_exclude = ['children', 'value', 'span', 'wrapped_tokens']

    def visualize(self, mode : VisualizingMode):
        self.id = 0
        self.graph = g.Digraph(f"Visualizing of {self.file_name}")

        if mode == VisualizingMode.AST:
            self.visualize_('Root', self.root, self.visualize_ast)
        elif mode == VisualizingMode.EXECUTION:
            self.visualize_('Root', self.root, self.visualize_execution)
        self.graph.render(f'{self.output}{mode}')

    def visualize_(self, node_name: str, node: nodes.Node, handler) -> str:
        key = self.add_node(node_name, node)
        children = self.get_children(node)
        
        if isinstance(node, nodes.WrapperNode):
            return key

        return handler(key, node, children)
    
    def visualize_ast(self, key: str, node: nodes.Node, children: list) ->  str:
        if len(children) == 0 and hasattr(node, 'children'):
            for child in node.children:
                child_key = self.visualize_('', child, self.visualize_ast)
                self.graph.edge(key, child_key)
        else:
            for name, child in children:
                if child is None:
                    continue
                child_key = self.visualize_(name, child, self.visualize_ast)
                self.graph.edge(key, child_key)
        return key

    def visualize_execution(self, key: str, node: nodes.Node, children: list) ->  str:
        #WIP
        child_keys: List[str] = []
        if len(children) == 0 and hasattr(node, 'children'):
            for child in node.children:
                child_keys.append(self.visualize_('', child, self.visualize_execution))
        else:
            for name, child in children:
                if child is None:
                    continue
                child_keys.append(self.visualize_(name, child, self.visualize_execution))

        if len(child_keys) > 0:
            self.graph.edge(key, child_keys[0])
            for index in range(1, len(child_keys)):
                current = child_keys[index]
                prev = child_keys[index - 1]
                self.graph.edge(prev, current)
        return key

    def add_node(self, node_name: str, node: nodes.Node) -> str:
        key = str(self.id)
        node_name = node_name.capitalize() if len(node_name) > 0 else node.__class__.__name__
        self.graph.node(key, f'{node_name}\n\n{self.get_text_for_node(node)}')
        self.id += 1
        return key

    def get_children(self, node: nodes.Node) -> list:
        return list(filter(lambda x: x[0] not in self.fields_to_exclude, node.__dict__.items()))

    def get_text_for_node(self, node: nodes.Node) -> str:
        if isinstance(node, TokenType):
            return str(node)
        if isinstance(node, nodes.Root):
            return ''
        if issubclass(type(node), nodes.Terminal):
            return node.value
        else:
            return self.source_code[node.span.begin: node.span.end]
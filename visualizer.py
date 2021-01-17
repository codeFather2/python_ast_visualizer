from os import remove
import graphviz as g
import nodes
from typing import List, Tuple
from enum import Enum
from lexer_utils import TokenType
from logging import Logger

class VisualizingMode(Enum):
    AST = 0
    EXECUTION = 1

class Visualizer:

    def __init__(self, root : nodes.Root, file_name: str, source_code : str, output_file : str, logger : Logger) -> None:
        self.root = root
        self.file_name = file_name
        self.output = output_file if output_file and len(output_file) > 0 else 'output/output'
        self.logger = logger
        self.id = 0
        self.graph = g.Digraph(f"Visualizing of {file_name}")
        self.source_code = source_code
        self.fields_to_exclude = ['children', 'value', 'span', 'wrapped_tokens']
        self.parents = []

    def visualize(self, mode : VisualizingMode):
        self.id = 0
        self.graph = g.Digraph(f"Visualizing of {self.file_name}")

        if mode == VisualizingMode.AST:
            self.visualize_ast('Root', self.root)
        elif mode == VisualizingMode.EXECUTION:
            self.logger.info(f'{VisualizingMode.EXECUTION} status is WIP')
            self.visualize_execution('Root', self.root)
        self.graph.render(f'{self.output}{mode}')


    def visualize_ast(self, name: str, node: nodes.Node) ->  str:
        key = self.add_node(name, node)
        children = self.get_children(node)
        
        if isinstance(node, nodes.WrapperNode):
            return key

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

    def visualize_execution(self, name: str, node: nodes.Node) ->  List[str]:
        keys = [self.add_node(name, node)]
        self.parents.append(keys[0])
        children = self.get_children(node)

        if isinstance(node, nodes.WrapperNode) or issubclass(node.__class__, nodes.Expression):
            return keys[0]

        children_keys: List[str] = []
        if len(children) == 0 and hasattr(node, 'children'):
            for child in node.children:
                self.handle_child_execution(children_keys, child, '')
        else:
            for name, child in children:
                self.handle_child_execution(children_keys, child, name)

        if len(children_keys) > 0:
            first = children_keys[0]
            while isinstance(first, list):
                first = first[0]
            self.add_tails_to_head(keys, first)
            self.add_edges_by_list(children_keys)
        self.parents.pop()
        return [keys, children_keys[-1]]

    def handle_child_execution(self, keys, child, name):
        if child is None:
            return
        if isinstance(child, nodes.BlockStatement):
            keys.append(self.prepare_block_execution(child))
        elif isinstance(child, nodes.IfElseStatement):
            keys.append(self.prepare_if_execution(child))
        else:
            keys.append(self.visualize_execution(name, child))

    def prepare_if_execution(self, node : nodes.IfElseStatement):
        keys = []
        condition = self.visualize_execution('If', node.condition)
        keys.append(condition)

        true_b = None
        if isinstance(node.true_branch, nodes.BlockStatement):
            block_keys = self.prepare_block_execution(node.true_branch)[0]
            self.graph.edge(condition, block_keys[0])
            true_b = block_keys[-1]
        else:
            true_b = self.visualize_execution('True', node.true_branch)

        false_b = None
        if node.false_branch and isinstance(node.false_branch, nodes.BlockStatement):
            block_keys = self.prepare_block_execution(node.false_branch)[0]
            self.graph.edge(condition, block_keys[0])
            false_b = block_keys[-1]
        elif node.false_branch and isinstance(node.false_branch, nodes.IfElseStatement):
            false_b = self.prepare_if_execution(node.false_branch)[0]
            self.graph.edge(condition, false_b[0])
            false_b = false_b[-1]
        else:
            false_b = self.visualize_execution('False', node.false_branch) if node.false_branch else None

        self.graph.edge(self.parents[-1], condition)
        if false_b:
            return [true_b, false_b]
        else:
            return true_b

    def prepare_block_execution(self, node : nodes.BlockStatement):
        keys : List[str] = []
        for st in node.children:
            if isinstance(st, nodes.IfElseStatement):
                keys.append(self.prepare_if_execution(st))
            else:
                keys.append(self.visualize_execution('', st))
        self.add_edges_by_list(keys)
        if len(keys) == 2:
            self.graph.edge(self.parents[-1], keys[0])
            return keys[-1]

        return keys

    
    
    def add_edges_by_list(self, keys):

        for index in range(1, len(keys)):
                current = keys[index]
                prev = keys[index - 1]
                if isinstance(current, list):
                    self.add_tail_to_heads(prev, current)
                elif isinstance(prev, list):
                    self.add_tails_to_head(prev, current)
                else:
                    self.graph.edge(prev, current)

    def add_tail_to_heads(self, tail, heads):
        for head in heads:
            if isinstance(head, list):
                    continue
            elif isinstance(tail, list):
                self.add_tails_to_head(tail, head)
            else:
                self.graph.edge(tail, head)

    def add_tails_to_head(self, tails, head):
        for tail in tails[::-1]:
            if isinstance(tail, list):
                self.add_tails_to_head(tail, head)
            elif isinstance(head, list):
                self.add_tail_to_heads(tail, head)
            else:
                self.graph.edge(tail, head)

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
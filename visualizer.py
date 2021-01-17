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

class SubTree:
    def __init__(self, key, children, is_branching) -> None:
        self.key = key
        self.children = children
        self.branching = is_branching
    
    def __str__(self) -> str:
        return f'{str(self.keys)} {self.branching}'
    
    def __repr__(self) -> str:
        return self.__str__()

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
        self.all_keys = []

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

    def visualize_execution(self, name: str, node: nodes.Node) -> SubTree:
        key = self.add_node(name, node)
        children = self.get_children(node)

        if isinstance(node, nodes.WrapperNode) or issubclass(node.__class__, nodes.Expression):
            return SubTree(key, [], False)

        sub_trees: List[SubTree] = []
        if len(children) == 0 and hasattr(node, 'children'):
            for child in node.children:
                self.handle_child_execution(sub_trees, child, '')
        else:
            for name, child in children:
                self.handle_child_execution(sub_trees, child, name)

        if len(sub_trees) > 0:
            first = sub_trees[0]
            while first.key == None:
                first = first.children[0]
            self.graph.edge(key, first.key)
            self.add_edges_by_list(sub_trees)
        return SubTree(None, sub_trees, False)

    def handle_child_execution(self, sub_trees, child, name):
        if child is None:
            return
        elif isinstance(child, nodes.BlockStatement):
            st_keys = []
            for st in child.children:
                st_keys.append(self.visualize_execution('', st))
            self.add_edges_by_list(st_keys)
            sub_trees.append(SubTree(None, st_keys, False))
        elif isinstance(child, nodes.IfElseStatement):
            sub_trees.append(self.prepare_if_execution(child))
        else:
            sub_trees.append(self.visualize_execution(name, child))

    def prepare_if_execution(self, node : nodes.IfElseStatement):
        keys = []
        condition = self.visualize_execution('If', node.condition)
        keys.append(condition)
        branches = []
        true_b = None
        if isinstance(node.true_branch, nodes.BlockStatement):
            st_keys = []
            for st in node.children:
                st_keys.append(self.visualize_execution('', st))
            true_b = SubTree(None, st_keys, False)
        else:
            true_b = self.visualize_execution('True', node.true_branch)

        branches.append(true_b)
        false_b = None
        if node.false_branch and isinstance(node.false_branch, nodes.IfElseStatement):
            false_b = self.prepare_if_execution(node.false_branch)
            self.graph.edge(condition.key, false_b.key)
        elif isinstance(node.false_branch, nodes.BlockStatement):
            st_keys = []
            for st in node.children:
                st_keys.append(self.visualize_execution('', st))
            false_b = SubTree(None, st_keys, False)
        else:
            false_b = self.visualize_execution('False', node.false_branch) if node.false_branch else None

        if false_b:
            branches.append(false_b)
        condition.children = branches
        condition.branching = True
        return condition

    def add_edges_by_list(self, keys : List[SubTree]):
        for index in range(1, len(keys)):
            current = keys[index]
            prev = keys[index - 1]
            self.add_edge(prev, current)

    def add_edge(self, prev: SubTree, current: SubTree):
        curr_len = len(current.children)
        prev_len = len(prev.children)
        if curr_len == 0 and prev_len == 0:
            self.graph.edge(prev.key, current.key)
        elif not current.key:
            self.add_edge(prev, current.children[0])
        elif not prev.key:
            self.add_edge(prev.children[-1], current)
        elif prev.branching:
            for prev_child in prev.children:
                self.add_edge(prev_child, current)
        elif current.branching:
            for curr_child in current.children:
                self.add_edge(prev, curr_child)
        else:
            self.graph.edge(prev.key, current.key)

    def add_tail_to_heads(self, tail, heads):
        for head in heads.children:
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
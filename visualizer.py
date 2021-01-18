from os import remove
import graphviz as g
import nodes
from typing import List, Tuple
from enum import Enum
from lexer_utils import TokenType
from logging import Logger

class VisualizingMode(Enum):
    AST = 0
    CFG = 1

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
        self.definitions : List[str] = []

    def visualize(self, mode : VisualizingMode):
        self.id = 0
        self.graph = g.Digraph(f"Visualizing of {self.file_name}")

        if mode == VisualizingMode.AST:
            self.visualize_ast('Root', self.root)
        elif mode == VisualizingMode.CFG:
            self.visualize_cfg('Root', self.root)
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

    def visualize_cfg(self, name: str, node: nodes.Node) -> List[str]:
        keys = self.visualize_cfg_for_node(name, node)
        if keys:
            return keys

        return self.visualize_children(name, node)
    
    def visualize_children(self, name, node) -> List[str]:
        key = self.add_node(name, node)
        children = self.get_children(node)

        child_keys: List[SubTree] = []
        if len(children) == 0 and hasattr(node, 'children'):
            for child in node.children:
                if not child:
                    continue
                child_keys.append(self.visualize_cfg('', child))
        else:
            for name, child in children:
                if not child:
                    continue
                child_keys.append(self.visualize_cfg(name, child))

        if len(child_keys) > 0:
            first = child_keys[0]
            while isinstance(first, list):
                first = first[0]
            self.graph.edge(key, first)
            self.add_edges_by_list(child_keys)
        return [key, child_keys]

    def visualize_cfg_for_node(self, name, node: nodes.Node)-> List[str]:
        if isinstance(node, nodes.WrapperNode) or issubclass(node.__class__, nodes.Expression):
            return self.add_node(name, node)
        if isinstance(node, nodes.BlockStatement):
            st_keys = []
            for st in node.children:
                st_keys.append(self.visualize_cfg('', st))
            self.add_edges_by_list(st_keys)
            return [st_keys[0], st_keys[-1]] if len(st_keys) > 1 else st_keys
        if isinstance(node, nodes.IfElseStatement):
            return self.prepare_if_execution(node)
        if isinstance(node, nodes.ForStatement):
            return self.prepare_loop_execution('For', node.iterator, node.block)
        if isinstance(node, nodes.WhileStatement):
            return self.prepare_loop_execution('While', node.condition, node.block)
        if isinstance(node, nodes.DefinitionStatement):
            return self.prepare_def_execution(node)
        if isinstance(node, nodes.ReturnStatement):
            return self.prepare_return_execution(node)
        return None

    def prepare_loop_execution(self, keyword, iterator_condition, node_block):
        iterator = self.visualize_cfg(keyword, iterator_condition)
        block = self.visualize_cfg('', node_block)
        first = block[0]
        while isinstance(first, list):
            first = first[0]
        self.graph.edge(iterator, first, color='purple', label='Loop entry')
        last = block[-1]
        while isinstance(last[-1], list):
            last = last[-1]
        if isinstance(last, list):
            for st in last:
                self.graph.edge(st, iterator, color='blue', label='Iteration')
        else:
            self.graph.edge(last, iterator, color='blue', label='Iteration')
        return [iterator]

    def prepare_if_execution(self, node : nodes.IfElseStatement):
        keys = []
        condition = self.visualize_cfg('If', node.condition)
        keys.append(condition)
        branches = []
        true_b = self.visualize_cfg('True', node.true_branch)
        self.graph.edge(condition, true_b[0], label ='True', color = 'green')
        branches.append(true_b[-1])

        false_b = None
        if node.false_branch and isinstance(node.false_branch, nodes.IfElseStatement):
            false_b = self.prepare_if_execution(node.false_branch)
            self.graph.edge(condition, false_b[0], label ='False', color = 'red')
            false_b = false_b[-1]
        else:
            false_b = self.visualize_cfg('False', node.false_branch) if node.false_branch else None
            self.graph.edge(condition, false_b[0], label ='False', color = 'red')
            false_b = false_b[-1]

        if false_b:
            if isinstance(false_b, list):
                branches.extend(false_b)
            else:
                branches.append(false_b)
        return [condition, branches]

    def prepare_def_execution(self, node: nodes.DefinitionStatement) -> List[str]:
        def_title = f'{node.name}{self.get_text_for_node(node.signature)}'
        self.definitions.append(def_title)
        key = str(self.id)
        self.graph.node(key, def_title)
        self.id += 1
        body = self.visualize_cfg('', node.body)
        first = body[0]
        while isinstance(first, list):
            first = first[-1]
        self.graph.edge(key, first, color='purple', label='Definition entry')
        self.definitions.pop()
        return [key]
    
    def prepare_return_execution(self, node: nodes.ReturnStatement) -> List[str]:
        key = str(self.id)
        text = self.get_text_for_node(node)
        if len(self.definitions) > 0:
            text = f'Exit from {self.definitions[-1]}\n{text}'
        self.graph.node(key, text, color='red')
        self.id += 1
        return [key]

    def add_edges_by_list(self, keys : list):
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
                return
            else:
                self.graph.edge(tail, head)

    def add_tails_to_head(self, tails, head):
        for tail in tails[::-1]:
            if isinstance(head, list):
                self.add_tail_to_heads(tail, head)
            elif isinstance(tail, list):
                if len(tail) == 0:
                    return
                while isinstance(tail[-1], list):
                    tail = tail[-1]
                for t in tail:
                    self.graph.edge(t, head)
                return
            else:
                self.graph.edge(tail, head)
                return

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
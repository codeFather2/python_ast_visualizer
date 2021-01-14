import nodes
from typing import List
from lexer_utils import TokenType as tt
from lexer import Token
from parser_utils import compound_stmt_tokens
from logging import Logger, currentframe
from errors import ParsingError


class Parser:
    @property
    def current_token(self):
        return self._tokens[self._index] if self._index < self._tokens_len else None

    def __init__(self, tokens, logger: Logger) -> None:
        self._tokens: List[Token] = tokens
        self._index = 0
        self._tokens_len = len(tokens)
        self.logger = logger

    def parse(self) -> nodes.Root:
        result = self.file_input()
        return result

    def file_input(self) -> nodes.Root:
        children: List[nodes.Node] = []
        while token := self.current_token:
            if token.type == tt.EOF:
                break
            if token.type == tt.NEWLINE:
                self._index += 1
                continue
            child = self.statement()
            if not child:
                break
            children.append(child)
        span = None
        if len(children) == 0:
            span = None
        elif len(children) == 1:
            span = children[0].span
        else:
            span = union_spans(children[0].span, children[-1].span)

        return nodes.Root(span, children)

    def statement(self) -> nodes.Node:
        node: nodes.Statement = None
        try:
            if self.current_token.type in compound_stmt_tokens:
                node = self.compound_stmt()
            else:
                node = self.simple_stmt()
        except Exception as ex:
            self.logger.error(repr(ex))

        return node

    def compound_stmt(self) -> nodes.Statement:
        current = self.current_token
        c_type = current.type 
        if c_type == tt.FOR:
            return self.for_stmt()
        if c_type == tt.IF:
            return self.if_stmt()
        if c_type == tt.WHILE:
            return self.while_stmt()
        if c_type == tt.DEF:
            return self.def_stmt
        if c_type == tt.CLASS:
            return self.class_stmt()
        if c_type == tt.TRY:
            return self.try_stmt()
        if c_type == tt.WITH:
            return self.with_stmt()

        raise NotImplementedError('compound statement')

    def for_stmt(self) -> nodes.ForStatement:
        raise NotImplementedError('for_stmt')

    def if_stmt(self) -> nodes.ForStatement:
        raise NotImplementedError('if_stmt')

    def while_stmt(self) -> nodes.ForStatement:
        raise NotImplementedError('while_stmt')

    def def_stmt(self) -> nodes.ForStatement:
        raise NotImplementedError('def_stmt')

    def class_stmt(self) -> nodes.ForStatement:
        raise NotImplementedError('class_stmt')

    def try_stmt(self) -> nodes.ForStatement:
        raise NotImplementedError('try_stmt')

    def with_stmt(self) -> nodes.ForStatement:
        raise NotImplementedError('with_stmt')

    def simple_stmt(self) -> nodes.Node:
        children: List[nodes.Node] = []

        try:
            children.append(self.small_stmt())
            while self.current_token.type == tt.NEWLINE:  # TODO: handle last stmt
                self.move_next()
                children.append(self.small_stmt())
        except Exception as ex:
            self.logger.error(repr(ex))

        return children[0] if len(children) == 1 else nodes.CollectionNode(
            union_spans(children[0].span, children[-1].span), children)

    def small_stmt(self) -> nodes.Node:
        current = self.current_token
        if current.type == tt.RETURN:
            return self.return_stmt()
        if current.type in [tt.PASS, tt.BREAK, tt.CONTINUE]:
            return nodes.Terminal(current.span)
        if current.type == tt.DEL:
            raise NotImplementedError()
        if current.type == tt.YIELD:
            raise NotImplementedError()
        if current.type == tt.ASSERT:
            raise NotImplementedError()
        if current.type == tt.RAISE:
            raise NotImplementedError()
        if current.type == tt.GLOBAL:
            raise NotImplementedError()
        if current.type == tt.NONLOCAL:
            raise NotImplementedError()
        if current.type == tt.STAR:
            raise NotImplementedError()

        assignment_expr = self.assignment()
        if not assignment_expr:
            return self.star_expressions()
        else:
            return assignment_expr

    def assignment(self) -> nodes.AssignmentExpression:
        left = self.atom()
        operator = self.assign_op()
        right = self.atom()
        return nodes.AssignmentExpression(union_spans(left.span, right.span), left, operator, right)

    def atom(self) -> nodes.Terminal:
        current = self.current_token
        self.move_next()
        if current.type == tt.NAME:
            return nodes.IdToken(current.span, current.value)
        if current.type == tt.STRING:
            return nodes.StringLiteral(current.span, current.value)
        if current.type == tt.NUMBER:
            return nodes.NumberLiteral(current.span, current.value)
        raise NotImplementedError(f'atom with value {current.value}')

    def assign_op(self) -> nodes.OperatorLiteral:
        current = self.current_token
        if current.type.value >= tt.ASSIGN.value and current.type.value <= tt.IDIV_ASSIGN.value:
            self.move_next()
            return nodes.OperatorLiteral(current.span, current.value)
        raise NotImplementedError(f'assign_op with value {current.value}')

    def return_statement(self) -> nodes.ReturnStatement:
        keyword : Token = self.current_token
        self.move_next()
        node : nodes.Expression= self.star_expressions()
        return nodes.ReturnStatement(nodes.TextSpan(keyword.position, node.span.end - keyword.position), node)

    def move_next(self):
        self._index += 1

    def right_token(self, offset: int = 1):
        index = self._index + offset
        return self._tokens[index] if index < self._tokens_len else None
    
    def lef_token(self, offset: int = 1):
        index = self._index + offset
        return self._tokens[index] if index >= 0 else None

    def match(self, token_type: int, token: Token):
        return token_type == token.type


def union_spans(s1: nodes.TextSpan, s2: nodes.TextSpan) -> nodes.TextSpan:
    begin = s1.begin if s1.begin > s2.begin else s2.begin
    end = s1.end if s1.end > s2.end else s2.end

    return nodes.TextSpan(begin, begin - end)

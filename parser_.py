import re
import nodes
from typing import List
from lexer_utils import TokenType as tt
from lexer import Token
from parser_utils import compound_stmt_tokens, comparison_tokens
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
        return self.file_input()

    def file_input(self) -> nodes.Root:
        children: List[nodes.Node] = []
        while token := self.current_token:
            if token.type == tt.EOF:
                break
            if token.type == tt.NEWLINE:
                self.move_next()
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
        keyword = self.current_token
        self.move_next()
        iterator : nodes.Expression = self.named_expr()
        block : nodes.BlockStatement = self.block()
        else_block = None
        if self.current_token.type == tt.ELSE:
            self.move_next()
            else_block = self.block()
        
        span = union_spans(keyword.span, else_block.span if else_block else block.span)
        return nodes.ForStatement(span, iterator, block)

    def if_stmt(self) -> nodes.ForStatement:
        if_keyword = self.current_token
        self.move_next()
        condition : nodes.Expression = self.named_expr()
        true_branch : nodes.Statement= self.block()
        false_branch = None
        if self.current_token.type  == tt.ELIF:
            false_branch = self.if_stmt()
        elif self.current_token.type == tt.ELSE:
            self.move_next()
            false_branch = self.block()

        span = None
        if false_branch:
            span = union_spans(if_keyword.span, false_branch.span)
        else:
            span = union_spans(if_keyword.span, true_branch.span)

        return nodes.IfElseStatement(span, if_keyword.value, condition, true_branch, false_branch)

    def while_stmt(self) -> nodes.ForStatement:
        keyword = self.current_token
        self.move_next()
        condition : nodes.Expression = self.named_expr()
        block : nodes.Statement = self.block()
        else_block = None
        if self.current_token.type == tt.ELSE:
            self.move_next()
            else_block = self.block()
        
        span = union_spans(keyword.span, else_block.span if else_block else block.span)
        return nodes.WhileStatement(span, condition, block)
    
    def block(self) -> nodes.Statement:
        #skip colon
        current = self.move_next()
        if current.type == tt.NEWLINE:
            statements : nodes.Node = []
            indent = self.move_next()
            if indent.type == tt.INDENT:
                self.move_next()
                while self.current_token.type != tt.DEDENT:
                    statements.append(self.statement())
            return nodes.BlockStatement(union_spans(indent.span, self.move_next().span), statements)
        else:
            return self.simple_stmt()
    
    def named_expr(self) -> nodes.Expression:
        if self.current_token.type == tt.NAME and self.right_token().type == tt.ASSIGN2:
            left = self.atom()
            op = self.assign_op()
            right = self.expression()
            return nodes.AssignmentExpression(union_spans(left.span, right.span), left, op, right)
        return self.expression()

    def expression(self) -> nodes.Expression:
        if self.current_token.type == tt.LAMBDA:
            raise NotImplementedError('lambda')
            return self.lambda_()
        expr = self.disjunction()
        if self.current_token.type == tt.IF:
            self.move_next() #skip if
            condition = self.disjunction()
            self.move_next() #skip else
            false_branch = self.expression()
            return nodes.ConditionalExpression(union_spans(expr.span, false_branch.span), condition, expr, false_branch)
        return expr

    def disjunction(self) -> nodes.Expression:
        return self.binary_by_priority(self.conjunction, [tt.OR])

    def conjunction(self) -> nodes.Expression:
        return self.binary_by_priority(self.inversion, [tt.AND])
    
    def inversion(self) -> nodes.Expression:
        if self.current_token.type == tt.NOT:
            not_token = self.current_token
            not_node = nodes.OperatorLiteral(not_token.span, not_token.value)
            self.move_next()
            expr = self.inversion()
            return nodes.UnaryOperatorExpression(union_spans(not_node.span, expr.span), not_node, expr)
        return self.comparison()

    def comparison(self) -> nodes.Expression:
        result = self.bitwise_or()
        current = self.current_token
        if current.type in comparison_tokens:
            op = nodes.OperatorLiteral(current.span, current.value)
            self.move_next()
            right = self.bitwise_or()
            return nodes.BinaryOperatorExpression(union_spans(result.span, right.span), result, op, right)
        elif current.type in [tt.NOT, tt.IN, tt.IS]:
            first_op_token = current
            op = None
            self.move_next()
            if (next_t := self.current_token).type in [tt.IN, tt.NOT]:
                op = nodes.OperatorLiteral(union_spans(first_op_token.span, next_t.span), f'{first_op_token.value} {next_t.value}')
            else:
                op = nodes.OperatorLiteral(first_op_token.span, first_op_token.value)
            right = self.bitwise_or()
            return nodes.BinaryOperatorExpression(union_spans(result.span, right.span), result, op, right)
        return result

    def bitwise_or(self) -> nodes.Expression:
        return self.binary_with_recursion(self.bitwise_xor, [tt.OR_OP])

    def bitwise_xor(self) -> nodes.Expression:
        return self.binary_with_recursion(self.bitwise_and, [tt.XOR])

    def bitwise_and(self) -> nodes.Expression:
        return self.binary_with_recursion(self.shift_expr, [tt.AND_OP])

    def shift_expr(self) -> nodes.Expression:
        return self.binary_with_recursion(self.sum_, [tt.LEFT_SHIFT, tt.RIGHT_SHIFT])

    def sum_(self) -> nodes.Expression:
        return self.binary_with_recursion(self.term, [tt.ADD, tt.SUB])

    def term(self) -> nodes.Expression:
        return self.binary_with_recursion(self.factor, [tt.STAR, tt.DIV, tt.IDIV, tt.MOD, tt.AT])

    def factor(self) -> nodes.Expression:
        if (op_token := self.current_token) in [tt.ADD, tt.SUB, tt.NOT_OP]:
            op = nodes.OperatorLiteral(op_token.span, op_token.value)
            self.move_next()
            expr = self.power()
            return nodes.UnaryOperatorExpression(union_spans(op.span, expr.span), op, expr)
        return self.power()

    def power(self) -> nodes.Expression:
        return self.binary_with_recursion(self.await_primary, [tt.POWER])

    def await_primary(self) -> nodes.Expression:
        if (op_token := self.current_token).type == tt.AWAIT:
            op = nodes.OperatorLiteral(op_token.span, op_token.value)
            self.move_next()
            primary = self.primary()
            return nodes.UnaryOperatorExpression(union_spans(op.span, primary.span), op, primary)
        return self.primary()
    
    def primary(self) -> nodes.Expression:
        atom = self.atom()
        if (current := self.current_token).type == tt.DOT:
            name = self.move_next()
            return nodes.MemberReference(union_spans(atom.span, name.span), atom, nodes.IdToken(name.span, name.value))
        elif current.type == tt.OPEN_PAREN:
            args = self.generator_args()
            return nodes.InvocationExpression(union_spans(atom.span, args[-1].span), atom, args)
        elif current.type == tt.OPEN_BRACKET:
            raise NotImplementedError('primary atom with slices (indexer os slice)')
        return atom
    
    def generator_args(self) -> List[nodes.Expression]:
        #TODO: kwargs, generators, positional and keyword markers support
        open_paren = self.current_token
        parens_cnt = 1
        self.move_next()
        exprs : List[nodes.Expression] = [open_paren]
        while parens_cnt != 0:
            if self.current_token.type == tt.OPEN_PAREN:
                parens_cnt += 1
                exprs.append(self.current_token)
                self.move_next()
                continue
            elif self.current_token.type == tt.CLOSE_PAREN:
                parens_cnt -= 1
                exprs.append(self.current_token)
                self.move_next()
                continue
            if self.current_token.type == tt.COMMA:
                self.move_next()
                continue
            exprs.append(self.expression())
        return exprs

    def binary_with_recursion(self, next_handler, operators) -> nodes.Expression:
        left = next_handler()
        if (op_token := self.current_token).type in operators:
            op = nodes.OperatorLiteral(op_token.span, op_token.value)
            self.move_next()
            right = self.binary_by_priority(next_handler, operators)
            return nodes.BinaryOperatorExpression(union_spans(left.span, right.span), left, op, right)
        return left

    def binary_by_priority(self, next_handler, operator_types):
        result = next_handler()
        while self.current_token.type in operator_types:
            op_token = self.current_token
            op = nodes.OperatorLiteral(op_token, op_token.value)
            self.move_next()
            right = next_handler()
            result = nodes.BinaryOperatorExpression(union_spans(result.span, right.span), result, op, right)
        return result

    def def_stmt(self) -> nodes.ForStatement:
        raise NotImplementedError('def_stmt')

    def class_stmt(self) -> nodes.ForStatement:
        raise NotImplementedError('class_stmt')

    def try_stmt(self) -> nodes.ForStatement:
        raise NotImplementedError('try_stmt')

    def with_stmt(self) -> nodes.ForStatement:
        raise NotImplementedError('with_stmt')

    def simple_stmt(self) -> nodes.Node:
        try:
            result = self.small_stmt()
            newline = self.current_token
            if newline.type == tt.NEWLINE:
                self.move_next()
            elif newline.type not in [tt.DEDENT, tt.EOF]:
                raise ParsingError(index= newline.span.begin , msg = f'simple statement should end with ({tt.NEWLINE}, {tt.DEDENT}, {tt.EOF})')
            return result
        except Exception as ex:
            self.logger.error(repr(ex))

        return None

    def small_stmt(self) -> nodes.Node:
        current = self.current_token
        if current.type == tt.RETURN:
            return self.return_stmt()
        if current.type in [tt.PASS, tt.BREAK, tt.CONTINUE]:
            self.move_next()
            return nodes.Terminal(current.span, current.value)
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
        if current.type == tt.NONE:
            return nodes.NoneLiteral(current.span, current.value)
        if current.type == tt.PEGPARSER:
            return nodes.EasterEggLiteral(current.span, current.value)
        if current.type in [tt.TRUE, tt.FALSE]:
            return nodes.BooleanLiteral(current.span, current.value)
        raise NotImplementedError(f'atom with value {current}')

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

    def move_next(self) -> Token:
        self._index += 1
        return self._tokens[self._index] if self._index < self._tokens_len else None

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

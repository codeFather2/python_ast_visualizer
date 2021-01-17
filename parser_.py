import nodes
from typing import List
from lexer_utils import TokenType as tt
from lexer import Token, take_tokens_until_type
from parser_utils import compound_stmt_tokens, comparison_tokens, assign_tokens
from logging import Logger
from errors import ParsingError
from text_span import TextSpan, union_spans


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
            self.logger.error(f'{repr(ex)} {self.current_token.span}')

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
            return self.def_stmt()
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

    def def_stmt(self) -> nodes.DefinitionStatement:
        def_ = self.current_token
        name_token = self.move_next()
        name = nodes.IdToken(name_token.span, name_token.value)
        self.move_next()
        signature_line = take_tokens_until_type(self._tokens[self._index:], tt.COLON)
        signature = nodes.WrapperNode(union_spans(signature_line[0].span, signature_line[-1].span), signature_line)
        self.move_next(len(signature_line))
        block = self.block()
        return nodes.DefinitionStatement(union_spans(def_.span, block.span), name, signature, block)

    def class_stmt(self) -> nodes.Statement:
        raise NotImplementedError('class_stmt')

    def try_stmt(self) -> nodes.Statement:
        raise NotImplementedError('try_stmt')

    def with_stmt(self) -> nodes.Statement:
        raise NotImplementedError('with_stmt')

    def block(self) -> nodes.Statement:
        #skip colon
        current = self.move_next()
        if current.type == tt.NEWLINE:
            while self.current_token.type == tt.NEWLINE:
                self.move_next()
            statements : nodes.Node = []
            if self.current_token.type == tt.INDENT:
                self.move_next()
                while self.current_token.type != tt.DEDENT:
                    statements.append(self.statement())
                    while self.current_token.type == tt.NEWLINE:
                        self.move_next()
                self.move_next()
            return nodes.BlockStatement(union_spans(statements[0].span, statements[-1].span), statements)
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
            return self.lambda_()
        expr = self.disjunction()
        if self.current_token.type == tt.IF:
            self.move_next() #skip if
            condition = self.disjunction()
            self.move_next() #skip else
            false_branch = self.expression()
            return nodes.ConditionalExpression(union_spans(expr.span, false_branch.span), condition, expr, false_branch)
        return expr

    def lambda_(self) -> nodes.LambdaExpression:
        raise NotImplementedError('lambda_')

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
            args = self.slices()
            return nodes.IndexerExpression(union_spans(atom.span, args.span), atom, args)
        return atom

    def slices(self) -> nodes.CollectionExpression:
        open_bracket = self.current_token
        self.move_next()
        slices_ : nodes.Expression = [] 
        while self.current_token.type != tt.CLOSE_BRACKET:
            if self.current_token.type == tt.COMMA:
                continue
            slices_.append(self.slice_())
        close_bracket = self.current_token
        self.move_next()
        return nodes.CollectionExpression(union_spans(open_bracket.span, close_bracket.span), slices_)

    def slice_(self) -> nodes.SliceExpression:
        first_span = None
        last_span = None
        start = None
        stop = None
        step = None

        if self.current_token.type == tt.COLON:
            first_span = self.current_token.span
            self.move_next()
        else:
            start = self.disjunction()
            first_span = start.span
        
        if self.current_token.type == tt.COLON:
            last_span = self.current_token.span
            self.move_next()
        else:
            stop = self.disjunction()
            last_span = stop.span

        if self.current_token.type == tt.COLON:
            last_span = self.current_token.span
            self.move_next()
        elif self.current_token.type not in [tt.COMMA, tt.CLOSE_BRACKET]:
            step = self.disjunction()
            last_span = step.span

        return nodes.SliceExpression(union_spans(first_span, last_span), start, stop, step)
        



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
            self.move_next()

        return None

    def small_stmt(self) -> nodes.Node:
        current = self.current_token
        if current.type == tt.RETURN:
            return self.return_stmt()
        if current.type in [tt.PASS, tt.BREAK, tt.CONTINUE]:
            self.move_next()
            return nodes.Terminal(current.span, current.value)
        if current.type == tt.STAR:
            return self.star_expressions()
        if current.type == tt.DEL:
            raise NotImplementedError('del_stmt')
        if current.type == tt.YIELD:
            return self.yield_expr('yield_stmt')
        if current.type == tt.ASSERT:
            raise NotImplementedError('assert_stmt')
        if current.type == tt.RAISE:
            raise NotImplementedError('raise_stmt')
        if current.type in [tt.GLOBAL, tt.NONLOCAL]:
            raise NotImplementedError('global_nonlocal_stmt')

        assignment_expr = self.assignment()
        if not assignment_expr:
            return self.star_expressions()
        else:
            return assignment_expr
    
    def return_stmt(self) -> nodes.ReturnStatement:
        keyword = self.current_token
        self.move_next()
        expr = self.expression()
        return nodes.ReturnStatement(union_spans(keyword.span, expr.span), expr)

    def assignment(self) -> nodes.AssignmentExpression:
        current = self.current_token
        line = take_tokens_until_type(self._tokens[self._index : ], tt.NEWLINE)
        line_types = set(map(lambda x: x.type, line))
        if not set(assign_tokens) & set(line_types):
            return None #TODO: complete decomposition assignments. if time remains

        if current.type == tt.NAME and self.right_token().type == tt.COLON:
            return self.var_decl()
        left = self.atom()
        operator = self.assign_op()
        right = self.star_expressions()
        return nodes.AssignmentExpression(union_spans(left.span, right.span), left, operator, right)

    def var_decl(self) -> nodes.Expression:
        name = self.atom()
        self.move_next() #move next
        annotation = self.expression()
        assign_part = None
        assign_op = None
        if self.current_token.type == tt.ASSIGN:
            assign_op = nodes.OperatorLiteral(self.current_token.span, self.current_token.value)
            self.move_next()
            assign_part = self.annotated_rhs()

        if assign_part:
            span = union_spans(name.span, assign_part.span)
        else:
            span = union_spans(name.span, annotation.span)

        return nodes.AssignmentExpression(span, name, assign_op, assign_part, annotation)

    def annotated_rhs(self) -> nodes.Node:
        if self.current_token.type == tt.YIELD:
            return self.yield_expr()
        else:
            return self.star_expressions()

    def atom(self) -> nodes.Terminal:
        current = self.current_token
        current_t = current.type
        if current_t == tt.NAME:
            self.move_next()
            return nodes.IdToken(current.span, current.value)
        if current_t == tt.STRING:
            self.move_next()
            return nodes.StringLiteral(current.span, current.value)
        if current_t == tt.NUMBER:
            self.move_next()
            return nodes.NumberLiteral(current.span, current.value)
        if current_t == tt.NONE:
            self.move_next()
            return nodes.NoneLiteral(current.span, current.value)
        if current_t == tt.PEGPARSER:
            self.move_next()
            return nodes.EasterEggLiteral(current.span, current.value)
        if current_t in [tt.TRUE, tt.FALSE]:
            self.move_next()
            return nodes.BooleanLiteral(current.span, current.value)
        if current_t == tt.OPEN_PAREN:
            return self.tuple_group_generator()
        if current_t == tt.OPEN_BRACKET:
            return self.list_()
        if current_t == tt.OPEN_BRACE:
            return self.dict_()
        if current_t == tt.ELLIPSIS:
            return nodes.OperatorLiteral(current.span, current.value)
        raise NotImplementedError(f'atom with value {current}')

    def tuple_group_generator(self) -> nodes.Expression:
        line = take_tokens_until_type(self._tokens[self._index : ], tt.NEWLINE)
        line_types = list(map(lambda x: x.type, line))
        if tt.FOR in line_types:
            return self.generator()
        if tt.YIELD in line_types:
            return self.group()
        return self.tuple_()

    def list_(self) -> nodes.CollectionExpression:
        line = take_tokens_until_type(self._tokens[self._index : ], tt.NEWLINE)
        line_types = list(map(lambda x: x.type, line))
        if tt.FOR in line_types:
            return self.generator()
        
        open_bracket = self.current_token
        if (next_t := self.right_token()).type == tt.CLOSE_BRACKET:
            return nodes.CollectionExpression(TextSpan(open_bracket.span.begin, next_t.span.begin + 1), [])
        exprs = self.star_named_expressions()
        self.move_next() # skip close_bracket
        return nodes.CollectionExpression(union_spans(open_bracket.span, exprs[-1].span), exprs)

    def tuple_(self) -> nodes.CollectionExpression:
        open_paren = self.current_token
        if (next_t := self.right_token()).type == tt.CLOSE_PAREN:
            return nodes.CollectionExpression(TextSpan(open_paren.span.begin, next_t.span.begin + 1), [])
        exprs = self.star_named_expressions()
        return nodes.CollectionExpression(union_spans(open_paren.span, exprs[-1].span), exprs)

    def group(self) -> nodes.UnaryOperatorExpression:
        raise NotImplementedError('group')

    def generator(self) -> nodes.GeneratorExpression:
        raise NotImplementedError('generator')

    def dict_(self) -> nodes.GeneratorExpression:
        open_brace = self.current_token
        self.move_next()
        exprs : List[nodes.Expression] = []
        skip_tokens = [tt.NEWLINE, tt.INDENT, tt.DEDENT, tt.COMMA]
        while self.current_token.type != tt.CLOSE_BRACE:
            if self.current_token.type in skip_tokens:
                self.move_next()
                continue
            key = self.disjunction(),
            if isinstance(key, tuple):
                key = key[0]
            self.move_next() #skip colon
            value = self.disjunction()
            exprs.append(nodes.KeyValueExpression(union_spans(key.span, value.span), key, value))

        close_brace = self.current_token
        self.move_next()
        return nodes.CollectionExpression(union_spans(open_brace.span, close_brace.span), exprs)

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
        return nodes.ReturnStatement(TextSpan(keyword.position, node.span.end - keyword.position), node)

    def star_expressions(self) -> nodes.Node:
        exprs = [self.star_expression()]
        while self.current_token.type == tt.COMMA:
            self.move_next()
            exprs.append(self.star_expression())
        if len(exprs) == 1:
            return exprs[0]

        return nodes.CollectionNode(union_spans(exprs[0].span, exprs[-1].span), exprs)

    def star_named_expressions(self) -> nodes.Node:
        exprs = [self.star_named_expression()]
        while self.current_token.type == tt.COMMA:
            self.move_next()
            exprs.append(self.star_named_expression())
        if len(exprs) == 1:
            return exprs[0]

        return nodes.CollectionNode(union_spans(exprs[0].span, exprs[-1].span), exprs)

    def star_expression(self) -> nodes.Expression:
        if (op_token := self.current_token).type == tt.STAR:
            op = nodes.OperatorLiteral(op_token.span, op_token.value)
            expr = self.bitwise_or()
            return nodes.UnaryOperatorExpression(union_spans(op.span, expr.span), op, expr)
        return self.expression()

    def star_named_expression(self) -> nodes.Expression:
        if (op_token := self.current_token).type == tt.STAR:
            op = nodes.OperatorLiteral(op_token.span, op_token.value)
            expr = self.bitwise_or()
            return nodes.UnaryOperatorExpression(union_spans(op.span, expr.span), op, expr)
        return self.named_expr()

    def move_next(self, offset : int = 1) -> Token:
        self._index += offset
        return self._tokens[self._index] if self._index < self._tokens_len else None

    def right_token(self, offset: int = 1):
        index = self._index + offset
        return self._tokens[index] if index < self._tokens_len else None
    
    def lef_token(self, offset: int = 1):
        index = self._index + offset
        return self._tokens[index] if index >= 0 else None

    def match(self, token_type: int, token: Token):
        return token_type == token.type

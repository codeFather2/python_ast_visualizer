from typing import List

class TextSpan:
    def __init__(self, begin: int, length : int) -> None:
        self.begin = begin
        self.length = length
        self.end = begin + length

    def __str__(self) -> str:
        return f'[{self.begin}..{self.end}]'

    def __repr__(self) -> str:
        return self.__str__()

class BaseNode:
    def __init__(self, span: TextSpan) -> None:
        self.span = span

class Node(BaseNode):
    def __init__(self, span : TextSpan, children : List[BaseNode] = None) -> None:
        self.children = children if children else []
        super().__init__(span)
    
    def __str__(self) -> str:
        res = ' '.join(map(lambda x: x.__str__(), self.children))
        return res

    def __repr__(self) -> str:
        return self.__str__()

class CollectionNode(Node):
    def __init__(self, span: TextSpan, children: List[BaseNode] = []) -> None:
        super().__init__(span, children)

# for unsupported nodes
class WrapperNode(Node):
    def __init__(self, span: TextSpan, children: List[BaseNode] = []) -> None:
        super().__init__(span, children)

class Root(Node):
    def __init__(self, span: TextSpan, nodes: List[Node] = []) -> None:
        super().__init__(span, nodes)

class Expression(Node):
    def __init__(self, span: TextSpan, children: List[BaseNode] = []) -> None:
        super().__init__(span, children)

class Statement(Node):
    def __init__(self, span: TextSpan, children: List[BaseNode] = []) -> None:
        super().__init__(span, children)

class IfElseStatement(Statement):
    def __init__(self, span: TextSpan, keyword: str, condition : Expression, true_branch : Statement, false_branch : Statement) -> None:
        self.keyword = keyword
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch
        children = [condition, true_branch, false_branch] if false_branch else [condition, true_branch]
        super().__init__(span, children)
    
    def __str__(self) -> str:
        else_part = ''
        if isinstance(self.false_branch, IfElseStatement):
            else_part = self.false_branch.__str__()
        elif issubclass(self.false_branch.__class__, Statement):
            else_part = f'else {self.false_branch}'
        return f'{self.keyword} {self.condition.__str__()}: {self.true_branch.__str__()} {else_part}'

class BlockStatement(Statement):
    def __init__(self, span: TextSpan, children: List[BaseNode] = []) -> None:
        super().__init__(span, children)

class ForStatement(Statement):
    def __init__(self, span: TextSpan, iterator: Expression, block: BlockStatement) -> None:
        super().__init__(span, [iterator, block])
        self.iterator = iterator
        self.block = block
    
    def __str__(self) -> str:
        return f'for {self.iterator.__str__()}: {self.block.__str__()}'


class WhileStatement(Statement):
    def __init__(self, span: TextSpan, condition : Expression, block: BlockStatement) -> None:
        super().__init__(span, [condition, block])
        self.condition = condition
        self.block = block

class ReturnStatement(Statement):
    def __init__(self, span: TextSpan, return_expr: Expression) -> None:
        super().__init__(span, [return_expr])

class Terminal(Expression):
    def __init__(self, span: TextSpan, value: str) -> None:
        self.value = value
        super().__init__(span)

    def __str__(self) -> str:
        return self.value

class IdToken(Terminal):
    def __init__(self, span: TextSpan, value: str) -> None:
        super().__init__(span, value)

class StringLiteral(Terminal):
    def __init__(self, span: TextSpan, value: str) -> None:
        super().__init__(span, value)

class NumberLiteral(Terminal):
    def __init__(self, span: TextSpan, value: str) -> None:
        super().__init__(span, value)

class NoneLiteral(Terminal):
    def __init__(self, span: TextSpan, value: str = "None") -> None:
        super().__init__(span, value)

class BooleanLiteral(Terminal):
    def __init__(self, span: TextSpan, value: str) -> None:
        super().__init__(span, value)

class EasterEggLiteral(Terminal):
    def __init__(self, span: TextSpan, value: str = "__peg_parser__") -> None:
        super().__init__(span, value)

class OperatorLiteral(Terminal):
    def __init__(self, span: TextSpan, value: str) -> None:
        super().__init__(span, value)

class InvocationExpression(Expression):
    def __init__(self, span: TextSpan, target: Expression, arguments: List[Expression]) -> None:
        super().__init__(span, [target].extend(arguments))
        self.target = target
        self.open_paren = arguments[0]
        self.close_paren = arguments[-1]
        self.arguments = arguments[1:-1] if len(arguments) > 2 else []
    
    def __str__(self) -> str:
        res =  f'{self.target.__str__()}({", ".join(map(lambda x: x.__str__(), self.arguments))})'
        return res

class ConditionalExpression(Expression):
    def __init__(self, span: TextSpan, condition: Expression, true_branch: Expression, false_branch: Expression) -> None:
        super().__init__(span, [condition, true_branch, false_branch])
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch

class BinaryOperatorExpression(Expression):
    def __init__(self, span: TextSpan, left: Expression, operator: OperatorLiteral, right: Expression) -> None:
        super().__init__(span, [left, operator, right])

class UnaryOperatorExpression(Expression):
    def __init__(self, span: TextSpan, operator: OperatorLiteral, expr: Expression) -> None:
        super().__init__(span, [operator, expr])
        self.operator = operator
        self.expr = expr

class AssignmentExpression(Expression):
    def __init__(self, span: TextSpan, left: Expression, operator: OperatorLiteral, right: Expression) -> None:
        super().__init__(span, [left, operator, right])

class IndexerExpression(Expression):
    def __init__(self, span: TextSpan, target: Expression, index: Expression) -> None:
        super().__init__(span, [target, index])
        self.target = target
        self.index = index

class MemberReference(Expression):
    def __init__(self, span: TextSpan, target: Expression, member: IdToken) -> None:
        super().__init__(span, [target, member])
        self.target = target
        self.member = member


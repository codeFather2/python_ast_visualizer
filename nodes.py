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

class BlockStatement(Statement):
    def __init__(self, span: TextSpan, children: List[BaseNode] = []) -> None:
        super().__init__(span, children)

class ForStatement(Statement):
    def __init__(self, span: TextSpan, iterator: Expression, in_expression: Expression, block: BlockStatement) -> None:
        super().__init__(span, [iterator, in_expression, block])
        self.iterator = iterator
        self.in_expression = in_expression
        self.block = block

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

class OperatorLiteral(Terminal):
    def __init__(self, span: TextSpan, value: str) -> None:
        super().__init__(span, value)

class InvocationExpression(Expression):
    def __init__(self, span: TextSpan, target: Expression, arguments: List[Expression]) -> None:
        super().__init__(span, [target].extend(arguments))
        self.target = target
        self.arguments = arguments

class BinaryOperatorExpression(Expression):
    def __init__(self, span: TextSpan, left: Expression, operator: OperatorLiteral, right: Expression) -> None:
        super().__init__(span, [left, operator, right])

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


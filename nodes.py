from typing import List
from text_span import TextSpan, union_spans

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
    def __init__(self, span: TextSpan, children = []) -> None:
        super().__init__(span, children)

# for unsupported nodes
class WrapperNode(Node):
    def __init__(self, span: TextSpan, children: List[BaseNode] = []) -> None:
        super().__init__(span, children)

class Root(Node):
    def __init__(self, span: TextSpan, nodes: List[Node] = []) -> None:
        super().__init__(span, nodes)
    
    def __str__(self) -> str:
        return self.__class__.__name__

class Expression(Node):
    def __init__(self, span: TextSpan, children: List[BaseNode] = []) -> None:
        super().__init__(span, children)

class Statement(Node):
    def __init__(self, span: TextSpan, children: List[BaseNode] = []) -> None:
        super().__init__(span, children)

class IfElseStatement(Statement):
    def __init__(self, span: TextSpan, keyword: str, condition : Expression, true_branch : Statement, false_branch : Statement) -> None:
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch
        children = [condition, true_branch, false_branch] if false_branch else [condition, true_branch]
        super().__init__(span, children)

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

class YieldStatement(Statement):
    def __init__(self, span: TextSpan, return_expr: Expression) -> None:
        super().__init__(span, [return_expr])

class AwaitStatement(Statement):
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

class LambdaExpression(Expression):
    def __init__(self, span: TextSpan, params : CollectionNode, expr : Expression ) -> None:
        children = params.children.copy()
        children.append(expr)
        super().__init__(span, children)
        self.params = params
        self.expr = expr

class InvocationExpression(Expression):
    def __init__(self, span: TextSpan, target: Expression, arguments: List[Expression]) -> None:
        self.target = target
        prepared_args = arguments[1:-1] if len(arguments) > 2 else []
        self.arguments = CollectionNode(union_spans(arguments[0].span, arguments[-1].span), prepared_args)
        super().__init__(span, [target, self.arguments])

    def __str__(self) -> str:
        return f'{self.target.__str__()}({", ".join(map(lambda x: x.__str__(), self.arguments))})'

    def __repr__(self) -> str:
        return self.__str__()

class ConditionalExpression(Expression):
    def __init__(self, span: TextSpan, condition: Expression, true_branch: Expression, false_branch: Expression) -> None:
        super().__init__(span, [condition, true_branch, false_branch])
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch

class BinaryOperatorExpression(Expression):
    def __init__(self, span: TextSpan, left: Expression, operator: OperatorLiteral, right: Expression) -> None:
        super().__init__(span, [left, operator, right])
        self.left = left
        self.operator = operator
        self.right = right

class UnaryOperatorExpression(Expression):
    def __init__(self, span: TextSpan, operator: OperatorLiteral, expr: Expression) -> None:
        super().__init__(span, [operator, expr])
        self.operator = operator
        self.expr = expr

class GeneratorExpression(Statement):
    def __init__(self, span: TextSpan, expr: Expression, iterator: Expression, conditions: List[Expression]) -> None:
        super().__init__(span, [expr, iterator].extend(conditions))
        self.expr = expr
        self.iterator = iterator
        self.conditions = CollectionNode(union_spans(conditions[0].span, conditions[-1].span), conditions)

    def __str__(self) -> str:
        conditions_str = ' if '.join(map(lambda x: x.__str__(), self.conditions)) if len(self.conditions) > 0 else ''
        return f'{self.expr.__str__()} for {self.iterator.__str__()} {conditions_str}'

class AssignmentExpression(Expression):
    def __init__(self, span: TextSpan, left: Expression, operator: OperatorLiteral, right: Expression, annotation: Expression = None) -> None:
        super().__init__(span, [left, operator, right])
        self.left = left
        self.annotation = annotation
        self.operator = operator
        self.right = right

class IndexerExpression(Expression):
    def __init__(self, span: TextSpan, target: Expression, index: Expression) -> None:
        super().__init__(span, [target, index])
        self.target = target
        self.index = index

class CollectionExpression(Expression):
    def __init__(self, span: TextSpan, elements: List[Expression]) -> None: #list, dict, tuple, generator
        super().__init__(span, elements)

class MemberReference(Expression):
    def __init__(self, span: TextSpan, target: Expression, member: IdToken) -> None:
        super().__init__(span, [target, member])
        self.target = target
        self.member = member


class DefinitionStatement(Statement):
    def __init__(self, span: TextSpan, name: IdToken, parameters: CollectionNode, body: Statement) -> None:
        children = [name]
        children.extend(parameters.children.copy())
        children.append(body)
        super().__init__(span, children=children)
        self.name = name
        self.parameters = parameters
        self.body = body

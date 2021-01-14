from enum import Enum

class TokenType(Enum):
    EOF = -1

    # Keywords
    DEF = 0
    RETURN = 1
    RAISE = 2
    FROM = 3
    IMPORT = 4
    AS = 5
    GLOBAL = 6
    ASSERT = 7
    IF = 8
    ELIF = 9
    ELSE = 10
    WHILE = 11
    FOR = 12
    IN = 13
    TRY = 14
    NONE = 15
    FINALLY = 16
    WITH = 17
    EXCEPT = 18
    LAMBDA = 19
    CLASS = 20
    YIELD = 21
    DEL = 22
    PASS = 23
    CONTINUE = 24
    BREAK = 25
    ASYNC = 26
    AWAIT = 27
    NONLOCAL = 28
    TRUE = 29
    FALSE = 30

    # Operators
    STAR = 31
    ADD = 32
    SUB = 33
    DIV = 34
    MOD = 35
    POWER = 36
    IDIV = 37

    # Assign
    ASSIGN = 38
    ASSIGN2 = 39
    ADD_ASSIGN = 40
    SUB_ASSIGN = 41
    MULT_ASSIGN = 42
    AT_ASSIGN = 43
    DIV_ASSIGN = 44
    MOD_ASSIGN = 45
    AND_ASSIGN = 46
    OR_ASSIGN = 47
    XOR_ASSIGN = 48
    LEFT_SHIFT_ASSIGN = 49
    RIGHT_SHIFT_ASSIGN = 50
    POWER_ASSIGN = 51
    IDIV_ASSIGN = 52

    # Comparison
    LESS_THAN = 53
    GREATER_THAN = 54
    EQUALS = 55
    GT_EQ = 56
    LT_EQ = 57
    NOT_EQ_1 = 58
    NOT_EQ_2 = 59

    # Logical
    OR = 60
    AND = 61
    NOT = 62
    IS = 63

    # Bitwise
    OR_OP = 64
    XOR = 65
    AND_OP = 66
    LEFT_SHIFT = 67
    RIGHT_SHIFT = 68
    NOT_OP = 69

    # Punctuators
    AT = 70
    DOT = 71
    ELLIPSIS = 72
    REVERSE_QUOTE = 73
    COMMA = 74
    COLON = 75
    SEMI_COLON = 76
    ARROW = 77

    OPEN_PAREN = 78
    CLOSE_PAREN = 79
    OPEN_BRACE = 80
    CLOSE_BRACE = 81
    OPEN_BRACKET = 82
    CLOSE_BRACKET = 83

    CONVERSION = 84
    NAME = 85
    STRING = 86
    FSTRING = 87
    RSTRING = 88
    NUMBER = 89
    FLOAT = 90

    COMMENT = 91
    INDENT = 92
    DEDENT = 93
    NEWLINE = 94


keywords = {
    'def': TokenType.DEF,
    'return': TokenType.RETURN,
    'raise': TokenType.RAISE,
    'from': TokenType.FROM,
    'import': TokenType.IMPORT,
    'as': TokenType.AS,
    'global': TokenType.GLOBAL,
    'assert': TokenType.ASSERT,
    'if': TokenType.IF,
    'elif': TokenType.ELIF,
    'else': TokenType.ELSE,
    'while': TokenType.WHILE,
    'for': TokenType.FOR,
    'in': TokenType.IN,
    'try': TokenType.TRY,
    'None': TokenType.NONE,
    'finally': TokenType.FINALLY,
    'with': TokenType.WITH,
    'except': TokenType.EXCEPT,
    'lambda': TokenType.LAMBDA,
    'class': TokenType.CLASS,
    'yield': TokenType.YIELD,
    'del': TokenType.DEL,
    'pass': TokenType.PASS,
    'continue': TokenType.CONTINUE,
    'break': TokenType.BREAK,
    'async': TokenType.ASYNC,
    'await': TokenType.AWAIT,
    'nonlocal': TokenType.NONLOCAL,
    'True': TokenType.TRUE,
    'False': TokenType.FALSE,
    'or': TokenType.OR,
    'and': TokenType.AND,
    'not': TokenType.NOT,
    'is': TokenType.IS
}

operators = {
    '+=': TokenType.ADD_ASSIGN,
    '-=': TokenType.SUB_ASSIGN,
    '*=': TokenType.MULT_ASSIGN,
    '@=': TokenType.AT_ASSIGN,
    '/=': TokenType.DIV_ASSIGN,
    '%=': TokenType.MOD_ASSIGN,
    '&=': TokenType.AND_ASSIGN,
    '|=': TokenType.OR_ASSIGN,
    '^=': TokenType.XOR_ASSIGN,
    '<<=': TokenType.LEFT_SHIFT_ASSIGN,
    '>>=': TokenType.RIGHT_SHIFT_ASSIGN,
    '**=': TokenType.POWER_ASSIGN,
    '//=': TokenType.IDIV_ASSIGN,
    '*': TokenType.STAR,
    '+': TokenType.ADD,
    '-': TokenType.SUB,
    '/': TokenType.DIV,
    '%': TokenType.MOD,
    '**': TokenType.POWER,
    '//': TokenType.IDIV,
    ':=':TokenType.ASSIGN2,
    '=': TokenType.ASSIGN,
    '<': TokenType.LESS_THAN,
    '>': TokenType.GREATER_THAN,
    '==': TokenType.EQUALS,
    '>=': TokenType.GT_EQ,
    '<=': TokenType.LT_EQ,
    '<>': TokenType.NOT_EQ_1,
    '!=': TokenType.NOT_EQ_2,
    '|': TokenType.OR_OP,
    '^': TokenType.XOR,
    '&': TokenType.AND_OP,
    '<<': TokenType.LEFT_SHIFT,
    '>>': TokenType.RIGHT_SHIFT,
    '~': TokenType.NOT_OP,
    '@': TokenType.AT,
}

punctuators = {
    '.': TokenType.DOT,
    '...': TokenType.ELLIPSIS,
    '`': TokenType.REVERSE_QUOTE,
    ',': TokenType.COMMA,
    ':': TokenType.COLON,
    ';': TokenType.SEMI_COLON,
    '->': TokenType.ARROW,
    '(': TokenType.OPEN_PAREN,
    ')': TokenType.CLOSE_PAREN,
    '{': TokenType.OPEN_BRACE,
    '}': TokenType.CLOSE_BRACE,
    '[': TokenType.OPEN_BRACKET,
    ']': TokenType.CLOSE_BRACKET
}
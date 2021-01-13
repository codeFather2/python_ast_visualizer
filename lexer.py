from errors import LexingError
from enum import Enum
import re


class Token:
    def __init__(self, token_type, value, position):
        self.token_type = token_type
        self.value = value
        self.position = position
        self.length = len(value) if value else 0

    def __str__(self):
        return f'({self.token_type}, {repr(self.value)})'

    def __repr__(self):
        return self.__str__()


trailing_tokens = [' ', '\n', '\r', '\t']
quotes = ['\'', '\"']

keyword_or_name_regex: re.Pattern = re.compile(r'(\w|_)([0-9]|\w|_)*')
number_regex: re.Pattern = re.compile(r'[1-9](\d)*')
operator_punctuator_regex: re.Pattern = re.compile(r'[^a-zA-Z0-9_]')
comment_regex: re.Pattern = re.compile(r'\#.*?([\r\n\f]|$)')


class Tokenizer:

    def __init__(self, text: str):
        self.text = text
        self.index = 0
        self.text_len = len(text)

    def tokenize(self) -> (list, LexingError):
        tokens: list = []
        error: LexingError = None
        while self.index < self.text_len:
            token, error = self.try_get_next_token()

            if error is not None:
                return (tokens, error)
            tokens.append(token)

        if tokens[-1].token_type != TokenType.EOF:
            tokens.append(Token(TokenType.EOF, None, self.text_len))
        return (tokens, error)

    def try_get_next_token(self) -> (Token, LexingError):
        try:
            return (self.next_token(), None)
        except LexingError as error:
            return (None, error)
        except Exception as ex:
            return (None, LexingError(ex, self.index))

    def next_token(self) -> Token:
        current = self.text[self.index]
        while current  in trailing_tokens:
            self.index += 1
            if self.index >= self.text_len:
                return Token(TokenType.EOF, None, self.text_len)
            current = self.text[self.index]
        token = None

        if current.isalpha() or current == '_':
            token = self.next_keyword_string_name()
        elif current.isnumeric():
            token = self.next_number()
        elif current in quotes:
            token = self.next_string()
        elif current == "#":
            token = self.next_comment()
        else:
            token = self.next_operator_punctuator()

        self.index += token.length
        return token

    def next_keyword_string_name(self) -> Token:
        next_ = self.get_next_symbol()
        if next_ and next_ in quotes:
            return next_string()

        token_text = self.get_token_text(keyword_or_name_regex)
        # Can be replaced by token_text.iskeyword()
        token_type = keywords.get(token_text, None)

        if token_type:
            return Token(token_type, token_text, self.index)
        else:
            return Token(TokenType.NAME, token_text, self.index)

    def next_string(self) -> Token:
        quote = None
        current_index = self.index
        inside_string = True
        while inside_string:
            current = self.get_symbol(current_index)
            if not current:
                break
            if current == quote and self.get_symbol(current_index - 1) != '\\':
                break
            if not quote and current in quotes:
                quote = current
            current_index += 1

        text_value = self.text[self.index: current_index + 1]
        return Token(TokenType.STRING, text_value, self.index)

    def next_number(self) -> Token:
        token_text = self.get_token_text(number_regex)
        return Token(TokenType.NUMBER, token_text, self.index)

    def next_comment(self) -> Token:
        token_text = self.get_token_text(comment_regex)
        # remove trailing control characters
        return Token(TokenType.COMMENT, token_text.rstrip(), self.index)

    def next_operator_punctuator(self) -> Token:
        token_text = self.get_token_text(operator_punctuator_regex)
        token_type = operators.get(token_text, None)
        if not token_type:
            token_type = punctuators.get(token_text, None)
        if not token_type:
            raise LexingError(index=self.index,
                              msg='Unexpected operator or punctuator')

        return Token(token_type, token_text, self.index)

    def get_token_text(self, regex: re.Pattern) -> Token:
        match: re.Match = regex.search(self.text, self.index)
        return self.text[match.start(): match.end()]

    def get_next_symbol(self) -> str:
        return self.get_symbol(self.index + 1)

    def get_current_symbol(self) -> str:
        return self.get_symbol(self.index)

    def get_prev_symbol(self) -> str:
        return self.get_symbol(self.index - 1)

    def get_symbol(self, index: int) -> str:
        return self.text[index] if index < self.text_len else None


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
    ADD_ASSIGN = 39
    SUB_ASSIGN = 40
    MULT_ASSIGN = 41
    AT_ASSIGN = 42
    DIV_ASSIGN = 43
    MOD_ASSIGN = 44
    AND_ASSIGN = 45
    OR_ASSIGN = 46
    XOR_ASSIGN = 47
    LEFT_SHIFT_ASSIGN = 48
    RIGHT_SHIFT_ASSIGN = 49
    POWER_ASSIGN = 50
    IDIV_ASSIGN = 51

    # Comparison
    LESS_THAN = 52
    GREATER_THAN = 53
    EQUALS = 54
    GT_EQ = 55
    LT_EQ = 56
    NOT_EQ_1 = 57
    NOT_EQ_2 = 58

    # Logical
    OR = 59
    AND = 60
    NOT = 61
    IS = 62

    # Bitwise
    OR_OP = 63
    XOR = 64
    AND_OP = 65
    LEFT_SHIFT = 66
    RIGHT_SHIFT = 67
    NOT_OP = 68

    # Punctuators
    AT = 69
    DOT = 70
    ELLIPSIS = 71
    REVERSE_QUOTE = 72
    COMMA = 73
    COLON = 74
    SEMI_COLON = 75
    ARROW = 76

    OPEN_PAREN = 77
    CLOSE_PAREN = 78
    OPEN_BRACE = 79
    CLOSE_BRACE = 80
    OPEN_BRACKET = 81
    CLOSE_BRACKET = 82

    CONVERSION = 83
    NAME = 84
    STRING = 85
    FSTRING = 86
    RSTRING = 87
    NUMBER = 88
    FLOAT = 89

    COMMENT = 90


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
    '*': TokenType.STAR,
    '+': TokenType.ADD,
    '-': TokenType.SUB,
    '/': TokenType.DIV,
    '%': TokenType.MOD,
    '**': TokenType.POWER,
    '//': TokenType.IDIV,
    '=': TokenType.ASSIGN,
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

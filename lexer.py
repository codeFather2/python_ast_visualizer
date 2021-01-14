from logging import Logger
from nodes import TextSpan
from errors import LexingError
from typing import Tuple, List
import re
from lexer_utils import TokenType, punctuators, operators, keywords


class Token:
    def __init__(self, token_type: int, value: str, position: int):
        self.type = token_type
        self.value = value
        length = len(value) if value else 0
        self.span = TextSpan(position, length)

    def __str__(self):
        return f'({self.type}, {repr(self.value)})'

    def __repr__(self):
        return self.__str__()


trailing_tokens = [' ', '\r', '\t']
quotes = ['\'', '\"']

keyword_or_name_regex: re.Pattern = re.compile(r'(\w|_)([0-9]|\w|_)*')
number_regex: re.Pattern = re.compile(r'[1-9](\d)*')
operator_punctuator_regex: re.Pattern = re.compile(r'([^a-zA-Z0-9_\s:])+|:| :=')
comment_regex: re.Pattern = re.compile(r'\#.*?([\r\n\f]|$)')


class Tokenizer:

    @property
    def _last_token(self) -> Token:
        return self._tokens[-1] if len(self._tokens) > 0 else None

    def __init__(self, text: str, logger: Logger):
        self.text = text
        self._index = 0
        self._text_len = len(text)
        self._indents = []
        self._tokens: List[Token] = []
        self.logger = logger

    def tokenize(self) -> Tuple[List[Token], LexingError]:
        error: LexingError = None
        while self._index < self._text_len:
            _, error = self.try_get_next_token()

            if error is not None:
                self.logger.error(error.msg)
                return (self._tokens, error)

        if self._tokens[-1].type != TokenType.EOF:
            self.handle_indenting()
            self._tokens.append(Token(TokenType.EOF, None, self._text_len))
        return (self._tokens, error)

    def try_get_next_token(self) -> Tuple[Token, LexingError]:
        try:
            self.next_token()
            return (self._last_token, None)
        except LexingError as error:
            return (None, error)
        except Exception as ex:
            return (None, LexingError(ex, self._index))

    def next_token(self):
        current_symbol = None

        last = self._last_token

        if last and last.type == TokenType.NEWLINE:
            self.handle_indenting()
            current_symbol = self.text[self._index]
        else:
            current_symbol = self.skip_trailing()
            if current_symbol is None:
                self.handle_indenting()
                self._tokens.append(Token(TokenType.EOF, None, self._text_len))
                return
        token = None

        if current_symbol == '\n':
            token = Token(TokenType.NEWLINE, current_symbol, self._index)
        elif current_symbol.isalpha() or current_symbol == '_':
            token = self.next_keyword_string_name()
        elif current_symbol.isnumeric():
            token = self.next_number()
        elif current_symbol in quotes:
            token = self.next_string()
        elif current_symbol == "#":
            token = self.next_comment()
        else:
            token = self.next_operator_punctuator()

        self._tokens.append(token)
        self._index += token.span.length

    def next_keyword_string_name(self) -> Token:
        next_ = self.get_next_symbol()
        if next_ and next_ in quotes:
            return self.next_string()

        token_text = self.get_token_text(keyword_or_name_regex)
        # Can be replaced by token_text.iskeyword()
        token_type = keywords.get(token_text, None)

        if token_type:
            return Token(token_type, token_text, self._index)
        else:
            return Token(TokenType.NAME, token_text, self._index)

    def next_string(self) -> Token:
        quote = None
        current_index = self._index
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

        text_value = self.text[self._index: current_index + 1]
        return Token(TokenType.STRING, text_value, self._index)

    def next_number(self) -> Token:
        token_text = self.get_token_text(number_regex)
        return Token(TokenType.NUMBER, token_text, self._index)

    def next_comment(self) -> Token:
        token_text = self.get_token_text(comment_regex)
        # remove trailing control characters
        return Token(TokenType.COMMENT, token_text.rstrip(), self._index)

    def next_operator_punctuator(self) -> Token:
        token_text = self.get_token_text(operator_punctuator_regex)
        token_type = operators.get(token_text, None)
        if not token_type:
            token_type = punctuators.get(token_text, None)
        if not token_type:
            raise LexingError(index=self._index,
                              msg='Unexpected operator or punctuator')

        return Token(token_type, token_text, self._index)

    def handle_indenting(self):
        indent_level = 0
        current_symbol = self.text[self._index] if self._index < self._text_len else None
        while current_symbol in trailing_tokens:
            if current_symbol == ' ':
                indent_level += 1
            elif current_symbol == '\t':
                indent_level += 4
            self._index += 1
            current_symbol = self.text[self._index] if self._index < self._text_len else None

        previous_indent = self._indents[-1] if len(self._indents) > 0 else 0

        if indent_level > previous_indent:
            self._indents.append(indent_level)
            self._tokens.append(Token(TokenType.INDENT, '', 0))
        else:
            while len(self._indents) > 0 and self._indents[-1] > indent_level:
                self._tokens.append(Token(TokenType.DEDENT, '', 0))
                self._indents.pop()

    def skip_trailing(self):
        current = self.text[self._index]
        while current in trailing_tokens:
            self._index += 1
            if self._index >= self._text_len:
                return None
            current = self.text[self._index]
        return current

    def get_token_text(self, regex: re.Pattern) -> Token:
        match: re.Match = regex.search(self.text, self._index)
        return self.text[match.start(): match.end()]

    def get_next_symbol(self) -> str:
        return self.get_symbol(self._index + 1)

    def get_current_symbol(self) -> str:
        return self.get_symbol(self._index)

    def get_prev_symbol(self) -> str:
        return self.get_symbol(self._index - 1)

    def get_symbol(self, index: int) -> str:
        return self.text[index] if index < self._text_len else None

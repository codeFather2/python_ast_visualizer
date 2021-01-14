# POC of prediction (WIP)
import re
from lexer_utils import TokenType as tt
from enum import Enum

rules = {
}

rules['literal'] = f'{tt.STRING.value}|{tt.NUMBER.value}'
rules['assign_op'] = f'[35-51]' #from TokenType.ASSIGN to TokenType.IDIVASSIGN
rules['assignment_part'] = f'{rules["assign_op"]}({rules["literal"]}|{tt.NAME.value})'
rules['assignment'] = f'({tt.NAME.value} {rules["assignment_part"]}?)'
rules['small_stmt'] = f'{rules["assignment"]}'
rules['statement'] = f'{rules["small_stmt"]}'
rules['file_input'] = f'{rules["statement"]}({tt.SEMI_COLON.value}{rules["statement"]})*'

class Possibility(Enum):
    One = 0
    OneAndMore = 1
    OneOrZero = 2
    ZeroOrMore = 3
pos = Possibility

class BaseRule:
    def __init__(self) -> None:
        return None

class TerminalRule(BaseRule):
    def __init__(self, name : str, elements : List[int, Possibility]) -> None:
        self.name = name
        self.elements = elements

class Rule(BaseRule):
    def __init__(self, name : str, alternatives_names : List[Tuple[BaseRule, Possibility]]) -> None:
        self.name = name
        self.alts = alternatives_names

def get_rules() -> List[BaseRule]:

    raise NotImplementedError()
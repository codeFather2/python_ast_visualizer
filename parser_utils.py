#POC of prediction (WIP)
from enum import Enum
from lexer_utils import TokenType as tt
from typing import List, Tuple
import re

compound_stmt_tokens = [tt.FOR, tt.DEF, tt.IF, tt.CLASS, tt.WITH, tt.TRY, tt.WHILE]
comparison_tokens = [tt.EQUALS, tt.NOT_EQ_1, tt.NOT_EQ_2, tt.LT_EQ, tt.LESS_THAN, tt.GT_EQ, tt.GREATER_THAN]
operator_tokens = [
    tt.STAR,
    tt.ADD,
    tt.SUB,
    tt.DIV,
    tt.MOD,
    tt.POWER,
    tt.IDIV,
    tt.LESS_THAN,
    tt.GREATER_THAN,
    tt.EQUALS,
    tt.GT_EQ,
    tt.LT_EQ,
    tt.NOT_EQ_1,
    tt.NOT_EQ_2,
    tt.OR_OP,
    tt.XOR,
    tt.AND_OP,
    tt.LEFT_SHIFT,
    tt.RIGHT_SHIFT,
    tt.NOT_OP,
    tt.AT,
]

unary_operator_tokens = [
    tt.DIV,
    tt.ADD,
    tt.NOT_OP
]
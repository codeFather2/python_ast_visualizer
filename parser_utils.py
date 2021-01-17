from lexer_utils import TokenType as tt

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

assign_tokens = [
    tt.ASSIGN,
    tt.ASSIGN2,
    tt.ADD_ASSIGN,
    tt.SUB_ASSIGN,
    tt.MULT_ASSIGN,
    tt.AT_ASSIGN,
    tt.DIV_ASSIGN,
    tt.MOD_ASSIGN,
    tt.AND_ASSIGN,
    tt.OR_ASSIGN,
    tt.XOR_ASSIGN,
    tt.LEFT_SHIFT_ASSIGN,
    tt.RIGHT_SHIFT_ASSIGN,
    tt.POWER_ASSIGN,
    tt.IDIV_ASSIGN
]

unary_operator_tokens = [
    tt.DIV,
    tt.ADD,
    tt.NOT_OP
]
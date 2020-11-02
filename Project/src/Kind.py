from enum import Enum


class Kind(Enum):

    KEYWORD = "keyword"
    IDEN = "identifier"
    TYPE = "type"
    LITERAL = "literal"
    MATH_OP = "operator"
    COMP_OP = "comparison_operator"
    BOOL_OP = "boolean_operator"
    DEL = "delimiter"
    PAR = "parentheses"
    ASSIGNMENT = "assignment"
    IF = "if"
    WHILE = "while"

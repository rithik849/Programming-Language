import ply.lex as lex
import re

tokens = ("INT",
        "FLOAT",
        "BOOL",
        "STRING",
        "DELIMITER",
        "MATH_OP",
        "BOOL_OP",
        "COMP_OP",
        "L_PAR",
        "R_PAR",
        "L_SCOPE",
        "R_SCOPE",
        "COMMA",
        "COL",
        "SEMI_COL")

def t_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_FLOAT(t):
    r'\d+[\.]\d+'
    t.value = float(t.value)
    return t

def t_BOOL(t):
    r'True|False'
    t.value = True if t.value=="True" else False
    return t

def t_STRING(t):
    r'/".*/"'
    t.value = str(t.value)

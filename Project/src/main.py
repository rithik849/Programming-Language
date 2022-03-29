#!/usr/local/bin/python3

from Parser import *

#Package argparse from python standard library
import argparse

#Parser for arguments being passed to command line command
parser = argparse.ArgumentParser()

#Arguments of the command. The filename being required while others are optional
parser.add_argument('-f','--filename',dest='filename',required =True ,help = "Enter the txt file of your program.")
parser.add_argument('-t','--parse_tree',action = "store_true",dest='parse_tree',default= False,help = "Use Flag if you want to view the parse tree")
parser.add_argument("-s",'--symbol_table',action = "store_true",dest='symbol_table',default = False, help = "Use Flag if you want to view the symbol table")
parser.add_argument('-p','--view_python',action = "store_true",dest='show_python',default = False,help = "Use Flag if you want to view the python code equivalant of the program")
parser.add_argument('-d','--duration',action = "store_true",dest='duration',default = False,help = "Use Flag if you want to see the duration of execution of the program")

args = parser.parse_args()

if args.filename:
    comp_file(args.filename,args.parse_tree,args.symbol_table,args.show_python,args.duration)


""" Internal class for extracting relevant strings from
    an ast parse tree, as a visitor."""

import ast

class InterestingStringCollector(ast.NodeVisitor):
    def __init__(self):
        self.suffixes = set()
        self.prefixes = set()
        self.fragments = set()
        self.fullStrings = set()


    def getCollectedStrings(self):
        return ( [ ( "SUFFIX", s ) for s in self.suffixes ] +
                 [ ( "PREFIX", s ) for s in self.prefixes ] +
                 [ ( "FRAGMENT", s ) for s in self.fragments ] +
                 [ ( "FULL", s ) for s in self.fullStrings ] )


    def visit_Compare(self, node):
        opstype = str(type(node.ops[0]))
        if opstype in ["<class '_ast.Eq'>","<class '_ast.NotEq'>"]:
            leftClass = str(type(node.left))
            rightClass = str(type(node.comparators[0]))
            if leftClass == "<class '_ast.Str'>" and rightClass != "<class '_ast.Str'>":
                self.fullStrings.add(node.left.s)
            elif leftClass != "<class '_ast.Str'>" and rightClass == "<class '_ast.Str'>":
                self.fullStrings.add(node.comparators[0].s)
        elif opstype == "<class '_ast.In'>":
            leftClass = str(type(node.left))
            comparatorsClass = str(type(node.comparators))
            if leftClass == "<class '_ast.Str'>":
                self.fragments.add(node.left.s)
            elif comparatorsClass == "<class 'list'>":
                for element in node.comparators[0].elts:
                    elementClass = str(type(element))
                    if elementClass == "<class '_ast.Str'>":
                        self.fullStrings.add(element.s)


    def visit_Call(self,node):
        if node.func.attr == "startswith" and str(type(node.args[0])) == "<class '_ast.Str'>":
            self.prefixes.add(node.args[0].s)
        elif node.func.attr == "endswith" and str(type(node.args[0])) == "<class '_ast.Str'>":
            self.suffixes.add(node.args[0].s)
        elif node.func.attr == "index" and str(type(node.args[0])) == "<class '_ast.Str'>":
            self.fragments.add(node.args[0].s)
        elif node.func.attr == "find" and str(type(node.args[0])) == "<class '_ast.Str'>":
            self.fragments.add(node.args[0].s)

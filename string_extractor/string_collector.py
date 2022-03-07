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


    def _isStringClass(self, c):
        className = str(type(c))
        if className in ["<class '_ast.Str'>", "<class 'str'>"]:
            return True
        elif ( className in [ "<class '_ast.Constant'>", "<class 'ast.Constant'>" ] and
               str(type(c.value)) == "<class 'str'>" ):
            return True
        else:
            return False

    def _isTupleClass(self, c):
        className = str(type(c))
        return className in  ["<class '_ast.Tuple'>", "<class 'ast.Tuple'>"]

    def _getStringValue(self, c):
        """Parses a single string value in the AST tree"""
        if str(type(c)) in ["<class '_ast.Str'>", "<class 'str'>"]:
            return c.s
        else:
            return c.value

    def _getStringValuesAsList(self, c):
        """Parses a single string value or tuple of strings in an AST
           tree as a list of strings."""
        def _get_single(c):
            classname = str(type(c))
            if classname in ["<class '_ast.Str'>", "<class 'str'>"]:
                return [c.s]
            elif classname in [ "<class '_ast.Constant'>", "<class 'ast.Constant'>" ]:
                return [c.value]
            else:
                return []

        classname = str(type(c))
        if classname in ["<class '_ast.Str'>", "<class 'str'>",
                         "<class '_ast.Constant'>", "<class 'ast.Constant'>"  ]:
            return _get_single(c)
        elif classname in ["<class '_ast.Tuple'>", "<class 'ast.Tuple'>"]:
            result = []
            for element in c.elts:
                result.extend(_get_single(element))
            return result

    def visit_Compare(self, node):
        opstype = str(type(node.ops[0]))
        if opstype in ["<class '_ast.Eq'>","<class '_ast.NotEq'>",
                       "<class 'ast.Eq'>"  ,"<class 'ast.NotEq'>" ]:
            left = node.left
            right = node.comparators[0]
            if self._isStringClass(left) and not self._isStringClass(right):
                self.fullStrings.add(self._getStringValue(left))
            elif (not self._isStringClass(left)) and self._isStringClass(right):
                self.fullStrings.add(self._getStringValue(right))
        elif opstype in ["<class '_ast.In'>", "<class 'ast.In'>"]:
            left = node.left
            comparators = node.comparators
            if self._isStringClass(left):
                self.fragments.add(self._getStringValue(left))
            elif str(type(comparators)) == "<class 'list'>":
                try:
                    elements = node.comparators[0].elts
                except AttributeError:
                    # Not a regular list
                    return
                for element in elements:
                    if self._isStringClass(element):
                        self.fullStrings.add(self._getStringValue(element))

    def visit_Call(self, node):
        try:
            attr = node.func.attr
            args = node.args
            arg0 = node.args[0]
        except AttributeError:
            # Call without attribute or first argument
            # is not a regular string
            return
        except IndexError:
            # Call without arguments
            return

        if attr == "startswith":
            for arg in node.args:
                if self._isStringClass(arg):
                    self.prefixes.add(self._getStringValue(arg))
                elif self._isTupleClass(arg):
                    self.prefixes.update(self._getStringValuesAsList(arg))
        elif attr == "endswith":
            for arg in node.args:
                if self._isStringClass(arg):
                    self.suffixes.add(self._getStringValue(arg))
                elif self._isTupleClass(arg):
                    self.suffixes.update(self._getStringValuesAsList(arg))
        elif attr == "index"    and self._isStringClass(arg0):
            self.fragments.add(self._getStringValue(arg0))
        elif attr == "find"     and self._isStringClass(arg0):
            self.fragments.add(self._getStringValue(arg0))

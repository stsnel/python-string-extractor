#!/usr/bin/env python3

import unittest

from string_extractor import StringExtractor

class TestStringExtractor(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.extractor = StringExtractor()

    def test_dummy(self):
        assert(True)

    def test_preprocess_jinja2(self):
        output = self.extractor._preprocessLine( "testfile_jinja.j2", 1)
        assert(output[0] == "IGNORE")

    def test_preprocess_one_line_statement(self):
        output = self.extractor._preprocessLine( "stringprocessor-testdata.py", 5)
        assert(output[0] == "OK")
        assert(output[1] == 'print("Hello")')

    def test_preprocess_two_line_statement_implicit(self):
        output = self.extractor._preprocessLine( "stringprocessor-testdata.py", 8)
        assert(output[0] == "OK")
        assert(output[1] == 'print( "Hello")')

    def test_preprocess_three_line_statement_implicit(self):
        output = self.extractor._preprocessLine( "stringprocessor-testdata.py", 12)
        assert(output[0] == "OK")
        assert(output[1] == 'print( "Hello" )')

    def test_preprocess_two_line_statement_explicit(self):
        output = self.extractor._preprocessLine( "stringprocessor-testdata.py", 17)
        assert(output[0] == "OK")
        assert(output[1] == 'print ("Hello")')

    def test_preprocess_three_line_statement_explicit(self):
        output = self.extractor._preprocessLine( "stringprocessor-testdata.py", 21)
        assert(output[0] == "OK")
        assert(output[1] == 'print ( "Hello")')

    def test_preprocess_if_statement(self):
        output = self.extractor._preprocessLine( "stringprocessor-testdata.py", 26)
        assert(output[0] == "OK")
        assert(output[1] == 'if foo == "bar":\n  pass')

    def test_preprocess_elif_statement(self):
        output = self.extractor._preprocessLine( "stringprocessor-testdata.py", 28)
        assert(output[0] == "OK")
        assert(output[1] == 'if foo == "baz":\n  pass')

    def test_preprocess_else_statement(self):
        output = self.extractor._preprocessLine( "stringprocessor-testdata.py", 30)
        assert(output[0] == "IGNORE")
        assert(output[1] == "")

    def test_preprocess_try_except(self):
        output = self.extractor._preprocessLine( "stringprocessor-testdata.py", 42)
        assert(output[0] == "IGNORE")
        assert(output[1] == "")
        output = self.extractor._preprocessLine( "stringprocessor-testdata.py", 44)
        assert(output[0] == "IGNORE")
        assert(output[1] == "")
        output = self.extractor._preprocessLine( "stringprocessor-testdata.py", 46)
        assert(output[0] == "IGNORE")
        assert(output[1] == "")

    def test_preprocess_while_statement(self):
        output = self.extractor._preprocessLine( "stringprocessor-testdata.py", 34)
        assert(output[0] == "OK")
        assert(output[1] == 'while foo == "bat":\n  pass')

    def test_preprocess_for_statement(self):
        output = self.extractor._preprocessLine( "stringprocessor-testdata.py", 38)
        assert(output[0] == "OK")
        assert(output[1] == 'for a in b:\n  pass')

    def test_comparison_equals_right(self):
        output = self.extractor.getInterestingStrings('a == "foo"')
        assert(len(output) == 1)
        assert(output[0][0] == "FULL")
        assert(output[0][1] == "foo")

    def test_comparison_equals_right_singlequotes(self):
        output = self.extractor.getInterestingStrings("a == 'foo'")
        assert(len(output) == 1)
        assert(output[0][0] == "FULL")
        assert(output[0][1] == "foo")

    def test_comparison_equals_right_with_comment(self):
        output = self.extractor.getInterestingStrings('a == "foo" # Compares variable a to "foo"')
        assert(len(output) == 1)
        assert(output[0][0] == "FULL")
        assert(output[0][1] == "foo")

    def test_comparison_notequals_right(self):
        output = self.extractor.getInterestingStrings('a != "foot"')
        assert(len(output) == 1)
        assert(output[0][0] == "FULL")
        assert(output[0][1] == "foot")

    def test_comparison_equals_left(self):
        output = self.extractor.getInterestingStrings('"foo" == a')
        assert(len(output) == 1)
        assert(output[0][0] == "FULL")
        assert(output[0][1] == "foo")

    def test_comparison_equals_nonstring(self):
        output = self.extractor.getInterestingStrings('a == 123')
        assert(len(output) == 0)

    def test_comparison_in(self):
        output = self.extractor.getInterestingStrings('"foo" in a')
        assert(len(output) == 1)
        assert(output[0][0] == "FRAGMENT")
        assert(output[0][1] == "foo")

    def test_call_startswith_single(self):
        output = self.extractor.getInterestingStrings('a.startswith("foo")')
        assert(len(output) == 1)
        assert(output[0][0] == "PREFIX")
        assert(output[0][1] == "foo")

    def test_call_startswith_tuple(self):
        output = self.extractor.getInterestingStrings('a.startswith( ("foo", "bar") )')
        assert(len(output) == 2)
        assert(output[0][0] == "PREFIX")
        assert(output[1][0] == "PREFIX")
        assert(sorted(list(map( lambda x : x[1], output ))) == ["bar", "foo"])

    def test_call_endswith_single(self):
        output = self.extractor.getInterestingStrings('a.endswith("foo")')
        assert(len(output) == 1)
        assert(output[0][0] == "SUFFIX")
        assert(output[0][1] == "foo")

    def test_call_endswith_tuple(self):
        output = self.extractor.getInterestingStrings('a.endswith( ("foo", "bar") )')
        assert(len(output) == 2)
        assert(output[0][0] == "SUFFIX")
        assert(output[1][0] == "SUFFIX")
        assert(sorted(list(map( lambda x : x[1], output ))) == ["bar", "foo"])

    def test_call_index(self):
        output = self.extractor.getInterestingStrings('a.index("foo")')
        assert(len(output) == 1)
        assert(output[0][0] == "FRAGMENT")
        assert(output[0][1] == "foo")

    def test_call_find(self):
        output = self.extractor.getInterestingStrings('a.find("foo")')
        assert(len(output) == 1)
        assert(output[0][0] == "FRAGMENT")
        assert(output[0][1] == "foo")

    def test_ternary(self):
        output = self.extractor.getInterestingStrings("a = 1 if foo == 'bar' else 2")
        assert(len(output) == 1)
        assert(output[0][0] == "FULL")
        assert(output[0][1] == "bar")

    def test_in_collection(self):
        output = self.extractor.getInterestingStrings('a in ["foo", "bar"]')
        assert(len(output) == 2)
        assert(output[0][0] == "FULL")
        assert(output[1][0] == "FULL")
        assert(sorted(list(map( lambda x : x[1], output ))) == ["bar", "foo"])

    def test_compound_statement(self):
        output = self.extractor.getInterestingStrings('a == "foo" or a =="bar"')
        assert(len(output) == 2)
        assert(output[0][0] == "FULL")
        assert(output[1][0] == "FULL")
        assert(sorted(list(map( lambda x : x[1], output ))) == ["bar", "foo"])

    def test_nested_compound_statement(self):
        output = self.extractor.getInterestingStrings('a == "foo" or ( a == "bar" and b == "bat" )')
        assert(len(output) == 3)
        assert(output[0][0] == "FULL")
        assert(output[1][0] == "FULL")
        assert(output[2][0] == "FULL")
        assert(sorted(list(map( lambda x : x[1], output ))) == ["bar", "bat", "foo"])

    def test_batch_base(self):
        lines = [ ( "stringprocessor-testdata.py", 26), ( "stringprocessor-testdata.py", 28) ]
        output = self.extractor.get_batch(lines)
        assert(len(output) == 2)
        assert(output[0][0] == "stringprocessor-testdata.py")
        assert(output[0][1] == 26)
        assert(output[0][2] == [ ( "FULL", "bar" ) ])
        assert(output[1][0] == "stringprocessor-testdata.py")
        assert(output[1][1] == 28)
        assert(output[1][2] == [ ( "FULL", "baz" ) ])

    def test_batch_collapsed(self):
        lines = [ ( "stringprocessor-testdata.py", 26), ( "stringprocessor-testdata.py", 28) ]
        output = self.extractor.get_batch(lines, True)
        assert(len(output) == 2)
        assert(output[0] == ( "FULL", "bar" ) )
        assert(output[1] == ( "FULL", "baz" ) )

    def test_batch_from_cache(self):
        lines = [ ( "stringprocessor-testdata.py", 26), ( "stringprocessor-testdata.py", 28) ]
        extractor = StringExtractor()
        extractor.cache = { ("stringprocessor-testdata.py", 26) : [ ("FULL", "cachedBar" ) ],
                            ("stringprocessor-testdata.py", 28) : [ ("FULL", "cachedBaz" ) ] }
        output = extractor.get_batch(lines)
        assert(len(output) == 2)
        assert(output[0][0] == "stringprocessor-testdata.py")
        assert(output[0][1] == 26)
        assert(output[0][2] == [ ( "FULL", "cachedBar" ) ])
        assert(output[1][0] == "stringprocessor-testdata.py")
        assert(output[1][1] == 28)
        assert(output[1][2] == [ ( "FULL", "cachedBaz" ) ])

    def test_batch_to_from_cache(self):
        # First save the results to persistent cache
        extractor = StringExtractor(True, "cache.test.tmp")
        extractor.cache = { ("stringprocessor-testdata.py", 26) : [ ("FULL", "retrievedBar" ) ],
                            ("stringprocessor-testdata.py", 28) : [ ("FULL", "retrievedBaz" ) ] }
        extractor.save()
        # Then retrieve them from cache in a new extractor
        lines = [ ( "stringprocessor-testdata.py", 26), ( "stringprocessor-testdata.py", 28) ]
        new_extractor = StringExtractor(True, "cache.test.tmp")
        output = new_extractor.get_batch(lines)
        assert(len(output) == 2)
        assert(output[0][0] == "stringprocessor-testdata.py")
        assert(output[0][1] == 26)
        assert(output[0][2] == [ ( "FULL", "retrievedBar" ) ])
        assert(output[1][0] == "stringprocessor-testdata.py")
        assert(output[1][1] == 28)
        assert(output[1][2] == [ ( "FULL", "retrievedBaz" ) ])

if __name__ == '__main__':
    unittest.main()

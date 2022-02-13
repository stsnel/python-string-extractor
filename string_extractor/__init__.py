#!/usr/bin/env python3

import ast
import linecache
import os
import pickle
import re

from string_extractor.string_collector import InterestingStringCollector

class StringExtractor:

    def __init__(self, use_cache = True, persistent_cache_file = None):
        self.cache_file = persistent_cache_file
        self.use_cache = use_cache
        if use_cache:
            if persistent_cache_file == None or not os.path.exists(persistent_cache_file):
                self.cache = {}
            else:
                with open(persistent_cache_file,"rb") as cache_file:
                    self.cache = pickle.load(cache_file)


    def save(self):
        """Saves the cache to file, if persistent cache is enabled."""
        if self.use_cache and self.cache_file != None:
            with open(self.cache_file, "wb") as cache_file:
                pickle.dump(self.cache, cache_file)

    def get_batch(self, lines, collapse_output = False):
        """ Gets a list of interesting string fragments.
            Arguments:
             - lines: a list of 2-tuples (file name + line number)
             - collapse output: determines output format.
                 true: output a common list of interesting strings as 2-tuples
                       ([PREFIX, SUFFIX, FRAGMENT, FULLSTRING], string)
                 false: outputs list of 3-tuples (file name, line number, output)
                       output can be one of:
                        "ERROR"
                        "IGNORE"
                        a list of 2-tuples with interesting strings for this line
        """
        output = []

        for (filename, line_number) in lines:
            if self.use_cache and (filename, line_number) in self.cache:
                 output.append( (filename, line_number, self.cache[(filename, line_number)]) )
                 continue

            pp_line = self._preprocessLine(filename, line_number)

            if pp_line[0] in ["ERROR", "IGNORE"]:
                result = pp_line[0]
            elif pp_line[0] == "OK":
                result = self.getInterestingStrings(pp_line[1])

            output.append( (filename, line_number, result) )

            if self.use_cache:
                self.cache[(filename, line_number)] = result

        if collapse_output:
            return self._collapse_batch_output(output)
        else:
            return output

    def _collapse_batch_output(self, output):
        result = { "FULL"       : {},
                   "PREFIX"     : {},
                   "SUFFIX"     : {},
                   "FRAGMENT"   : {} }

        for (filename, line_number, line_data) in output:
            if line_data in ["ERROR", "IGNORE"]:
                continue
            for (stringtype, stringdata) in line_data:
                result[stringtype][stringdata] = 1

        result_as_list = []
        for stringtype, typedata in result.items():
            for string in typedata:
                result_as_list.append( (stringtype, string) )

        return result_as_list


    def _preprocessLine(self, filename, lineNumber):
        """ Retrieves a line of code for parsing, checks whether it can be parsed
            and performs any transformations needed for dealing with control structures
            or multiline statements.
            
            Result is a 2-tuple, with the first element being a status code, and the second
            element being the preprocessed statement to be parsed.
            
            Status codes:
              OK           : line can be parsed
              IGNORE       : the parser should ignore this line, because the preprocessor
                             doesn't support this particular type of statement (in this context).
              ERROR        : the preprocessor was unable to transform the line into a
                             parsable form. This could happen for long multiline statements (length
                             more than maxMultilineLength), or for language constructs that aren't
                             recognized by the preprocessor.
            """
        maxMultilineLength= 20
        numberOfLines = self._getNumberOfLines(filename)
        line = linecache.getline(filename, lineNumber).strip()

        if filename.endswith(".j2"):
            return ("IGNORE","")

        # Ignore irrelevant control flow statements
        for keyword in ["try", "except", "finally", "else" ]:
            if re.match( "^{}\s*[\s:]$".format(keyword), line):
                return ("IGNORE", "")
            elif re.match( "^{}\s".format(keyword), line):
                return ("IGNORE", "")

        # Normalize elif statement to if statement.
        if re.match( "^elif\s", line):
            line = line[2:]

        # Check whether we are dealing with a relevant compound statement
        compoundStatement = False
        for keyword in ["for", "if", "while"]:
            if re.match( "^{}[\(\s]".format(keyword), line):
                compoundStatement = True

        statement = ""
        max_offset = max ( maxMultilineLength, numberOfLines - lineNumber )
        for offset in range(numberOfLines - lineNumber):
            thisLineNumber = lineNumber + offset

            if offset == 0:
                thisLine = line
            else:
                thisLine = linecache.getline(filename, thisLineNumber).strip()

            statement = " ".join([statement, thisLine ]).strip()

            if statement.endswith("\\"):
                # Explicit line continuation. Keep iterating over lines,
                # even if maximum statement length has been exceeded.
                statement = statement[:-1]
                continue
            elif compoundStatement and statement.endswith(":"):
                # It seems we have a complete control structure statement.
                # Add a dummy block.
                statementWithDummyBlock = statement + "\n  pass"
                if self._isParsable(statementWithDummyBlock):
                    return ("OK", statementWithDummyBlock)

            elif (not compoundStatement) and self._isParsable(statement):
                return ("OK", statement)

            if offset >= maxMultilineLength:
                break

        return ("ERROR", "")


    def _isParsable(self, statement):
        """Determines whether a statement is parsable."""
        try:
            tree = ast.parse(statement)
            return True
        except SyntaxError:
            return False


    def _getNumberOfLines(self, filename):
        with open(filename, 'r') as file:
            for count, line in enumerate(file):
                pass
        return count + 1

    def getInterestingStrings(self, statement):
        tree = ast.parse(statement)
        collector = InterestingStringCollector()
        collector.visit(tree)
        return collector.getCollectedStrings()


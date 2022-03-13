# python-string-extractor

Extracts strings relevant to control flow from Python code

This package extracts strings (including prefixes, suffixes and fragments)
from Python code that seem (potentially) relevant to control flow. 
Strings that are potentially relevant to the control flow can be used for
text input generation in scriptless testing, or for automated test case
generation.

For example, in the code fragment below, string literals "foo" and "bar" are relevant to
the control flow, since they are used in comparisons, so it might be useful to use
these string literals in test cases, or in input generation for scriptless testing.

```
if var == "foo":
   doSomething()
elif var == "bar":
   doSomethingElse()
```

## System requirements

Python-string-extractor currently works with Python 3.6 through 3.10.

## Overview of recognized functions and operators

|Node type | Function or operator | Type of constant extracted | Example expression|
|----------|----------------------|----------------------------| ------------------|
|Comparison | == (equals operator) | Full string | a == "foo" |
|Comparison | != (does not equal operator) | Full string | a != "foo" |
|Comparison | in (part of operator) | String fragment | "foo" in a |
|Comparison | in (match with collection) | List of full strings | a in ["foo","bar"] |
|Call | string.startswith | String prefix, or tuple of string prefixes  | a.startswith("foo") |
|Call | string.endswith | String suffix, or tuple of string suffixes  | a.endswith("foo") |
|Call | string.find | String fragment | a.find("foo") |
|Call | string.index | String fragment | a.index("foo") |

## Usage

The string extractor needs to be provided with a list of lines of code. This would
typically be an execution trace that is obtained using a trace function.

### Extracting strings from a single statement

This REPL example shows how to extract relevant strings from a single statement:

```
>>> from string_extractor import StringExtractor
>>> e = StringExtractor()
>>> e.extract_strings( 'var = "foo" if something == "baz" else "bar"' )
[('FULL', 'baz')]
>>>
```

### Extracting strings from lines of code in a Python file

The below example shows how to extract interesting strings from a list
of executed statements in a source file.

Consider the below source code file named `hello.py`:

```
#!/usr/bin/env python3

import sys

if sys.argv[1] == "english":
    print("Hello world!")
elif sys.argv[1] == "dutch":
    print("Hallo wereld!")
elif sys.argv[1] == "german":
    print("Hallo Welt!")
```

This REPL example shows how to extract strings potentially relevant to
code flow from some of the lines:

```
>>> from string_extractor import StringExtractor
>>> e = StringExtractor()
>>> e.get_batch ( [("hello.py", 5), ("hello.py", 7) , ("hello.py", 9)], True )
[('FULL', 'english'), ('FULL', 'dutch'), ('FULL', 'german')]
```

Remove the last boolean argument to `get_batch` in order to group the strings by
line of code:

```
>>> e.get_batch ( [("hello.py", 5), ("hello.py", 7) , ("hello.py", 9)] )
[('hello.py', 5, [('FULL', 'english')]), ('hello.py', 7, [('FULL', 'dutch')]), ('hello.py', 9, [('FULL', 'german')])]
```

### Collecting an execution trace and extracting relevant strings

The most practical way to obtain an execution trace from a Python program is
to add a trace function that logs the source file name and line
number of every executed line of code.

A modified version of the Coverage.py coverage measurement tool that also
collects execution traces is available at https://github.com/stsnel/coveragepy/tree/6.2-local/

The example below shows how to use the modified version of Coverage.py and the string extractor
in an existing script.

```
#!/usr/bin/env python3

from coverage import Coverage
from string_extractor import StringExtractor
import sys

def hello():
    if sys.argv[1] == "english":
        print("Hello world!")
    elif sys.argv[1] == "dutch":
        print("Hallo wereld!")
    elif sys.argv[1] == "german":
        print("Hallo Welt!")

c = Coverage()
c.start()
c.load(init=False)
c.switch_log_context("first_run")
hello()
extractor = StringExtractor()
strings = extractor.get_batch(c.export_execution_path("first_run"), True)
print(str(strings))
c.stop()
c.save()
```

In this example, the modified version of Coverage.py only collects relevant
strings from the script itself, not from any libraries it uses. In order
to also collect executed lines of code from libraries, create the Coverage object
in the following way: `c = Coverage(cover_pylib=True)`.

The example uses a log context named `first_run`. Log contexts
are a way to label all code that is subsequently executed as belonging to a
particular test case, program run, test program action, or other event. All
executed statements are labelled with the current log context, until the
log context is set to a different value.

### Collecting an execution trace from a Flask web application

An execution trace can be obtained from a web application by starting
the modified version of Coverage.py prior to each request and stopping it
afterwards. In a Flask web application, this can be done in a before_request
and after_request handler. An additional route could be added to the Flask
application for setting the log context, so that execution information can
be related to a particular test case by setting the log context prior to
executing the test case.

An example of such instrumentation on a web application can be found at
https://github.com/stsnel/ckan/tree/2.9.3-testar

## Cache settings

The string extractor caches strings extracted from lines by default. Caching extracted strings
increases efficiency, in particular when processing loops in execution traces, or when processing
execution traces for multiple requests or test cases that execute common code.

It's also possible to create a string extractor with no cache:

```
>>> e = StringExtractor(False)
```

The cache is non-persistent by default. It can be useful to persist the cache to file
in order to cache extracted strings across multiple executions of a program. If a StringExtractor
is created with a filename argument, the cache is loaded from file on creation of the StringExtractor.
The cache must be saved using the save() function after the StringExtractor has processed all lines.
For example:

```
>>> from string_extractor import StringExtractor
>>> e = StringExtractor(True, "/tmp/cache.dat")
>>> e.get_batch ( [("hello.py", 5), ("hello.py", 7) , ("hello.py", 9)] )
[('hello.py', 5, [('FULL', 'english')]), ('hello.py', 7, [('FULL', 'dutch')]), ('hello.py', 9, [('FULL', 'german')])]
>>> e.save()
```

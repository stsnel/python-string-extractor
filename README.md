# python-string-extractor

Extracts strings relevant to control flow from Python code

This package extracts strings (including prefixes, suffixes and fragments)
from Python code that seems (potentially) relevant to control flow. Having
a list of strings that are potentially relevant to the execution path can
help with scriptless testing or automated test case generation.

For, example in this code example strings "foo" and "bar" are relevant to
the control flow, so it might be useful to include them in test input for
the software.

```
if var == "foo":
   doSomething()
elif var == "bar":
   doSomethingElse()
```

## System requirements

Python-string-extractor currently works with Python 3.6 through 3.10.

## Usage

The string extractor needs to be provided with an execution trace of Python
software. This trace can be obtained using a trace function, or a modified
version of coverage measurement software.

The string extractor has a cache, which is enabled by default and can
optionally be persisted to a file. This helps with efficiently handling loops
in code, as well as overlapping execution traces.

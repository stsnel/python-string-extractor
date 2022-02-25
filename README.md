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

# Overview of recognized functions and operators

|Node type | Function or operator | Type of constant extracted | Example expression|
|----------|----------------------|----------------------------| ------------------|
|Comparison | == (equals operator) | Full string | a == "foo" |
|Comparison | != (does not equal operator) | Full string | a != "foo" |
|Comparison | in (part of operator) | String fragment | "foo" in a |
|Comparison | in (match with collection) | List of full strings | a in ["foo","bar"] |
|Call | string.startswith | String prefix | a.startswith("foo") |
|Call | string.endswith | String suffix | a.endswith("foo") |
|Call | string.find | String fragment | a.find("foo") |
|Call | string.index | String fragment | a.index("foo") |

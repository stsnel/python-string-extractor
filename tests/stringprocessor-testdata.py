#!/usr/bin/env python3


# Line 5: single-line statement
print("Hello")

# Line 8: two line statement with implicit continuation
print(
"Hello")

# Line 12: three line statement with implicit continuation
print(
"Hello"
)

# Line 17: two line statement with explicit continuation
print\
("Hello")

# Line 21: three line statement with explicit continuation
print\
(\
"Hello")

# Line 26: if statement / line 28 elif statement / line 30 else statement
if foo == "bar":
    print("Hello")
elif foo == "baz":
    print("Bye")
else:
    print("Hello")

# Line 34: while loop
while foo == "bat":
    print("Foo is bat")

# Line 38: for loop
for a in b:
    print("Foo bar")

# Line 42,44,46: try / except / finally
try:
    print("Foo")
except Exception as e:
    print("Bar")
finally:
    print("Baz")

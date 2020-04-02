"""
import io,sys

# if sys.stdin is empty, the user will be prompted for input
# sys.stdin = io.StringIO('')
sys.stdin = io.StringIO('Hello world')

r = sys.stdin.readline()
if not r:
    r = builtins.input()

print(r)
"""

import io,sys
s = io.StringIO('Hello, world!')
sys.stdin = s
sys.__stdin__ = s
r = input()
print(r)

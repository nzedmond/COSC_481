import sys

print(sys.version_info)
print(sys.version)

a = b'h\x65llo'
print(list(a))
print(a)

a = 'a\uO3OO propos'
print(list(a))
print(a)
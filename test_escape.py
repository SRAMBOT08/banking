# Test string escaping in Python
# In Python source code:
# - '\$hello' -> string containing backslash + dollar + hello (7 chars)
# - r'\$hello' -> string containing backslash + dollar + hello (7 chars)
# - We want just '$hello' (6 chars) in the final string

# To get '$hello' in the string from source code:
# Option 1: Just write '$hello' in source (no backslash)
# But Python 3.12+ warns about '\' in strings that aren't valid escapes

# Let's test:
s1 = '$hello'
print('s1:', repr(s1), 'len:', len(s1))

s2 = '\$hello'
print('s2:', repr(s2), 'len:', len(s2))

s3 = r'\$hello'
print('s3:', repr(s3), 'len:', len(s3))

# So the solution: just write '$hello' in source code!
# The warning about invalid escape sequence is for things like '\n', '\t', etc.
# But '$' is not a valid escape, so '\$' warns but works.

# For our queries, we should just use '$id' in the source, not '\$id'
# The f-strings will then have '$id' which Neo4j expects.
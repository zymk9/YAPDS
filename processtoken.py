import clang.cindex
import clang.enumerations
import sys
import csv

sys.path.extend(['.', '..'])

cursor_kind = clang.cindex.CursorKind
index = clang.cindex.Index.create()
tmp = index.parse('test1.cpp')
cursor = tmp.cursor

token_map = {}
processed = ''

with open('tokenmap.csv') as tokenmap:
    rows = csv.reader(tokenmap)
    for row in rows:
        token_map[row[0]] = row[1]
    #print token_map


def process_tokens(tokens):
    res = ''
    for token in tokens:
        #print token.cursor.kind.name
        in_map = token_map.get(token.cursor.kind.name)
        if in_map == None:
            res += chr(122)
        else:
            res += chr(int(token_map[token.cursor.kind.name]))
    return res


for child in cursor.get_children():
    if child.location.file.name != 'test1.cpp':
        continue
    if child.kind != cursor_kind.CXX_METHOD and child.kind != cursor_kind.FUNCTION_DECL:
        continue
    tokens = child.get_tokens()
    processed += process_tokens(tokens)
    # for token in tokens:
    #    print token.cursor.kind.name
    #res = process_tokens(tokens)
    #print ''

print processed

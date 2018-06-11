import clang.cindex
import clang.enumerations
import csv
from winnowing import winnow
from pycparser import c_parser, c_ast, parse_file
import re
import sys

sys.path.extend(['.', '..'])


def process_tokens(filename):
    cursor_kind = clang.cindex.CursorKind
    index = clang.cindex.Index.create()
    tmp = index.parse(filename)
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
        if child.location.file.name != filename:
            continue
        if child.kind != cursor_kind.CXX_METHOD and child.kind != cursor_kind.FUNCTION_DECL:
            continue
        tokens = child.get_tokens()
        processed += process_tokens(tokens)
        # for token in tokens:
        #    print token.cursor.kind.name
        #res = process_tokens(tokens)
        #print ''

    return processed


def ast_pre(path):
    file = open(path)
    content = file.read()
    file.close()
    patten = re.compile(r'#include[\s]*<[\s\S]*>\n')
    content = patten.sub('', content)
    patten = re.compile(r'using[\s]*namespace[\s]*[\S]*\n')
    content = patten.sub('', content)
    patten = re.compile(r'//[\S\t ]*\n')
    content = patten.sub('', content)
    patten = re.compile(r'/\*[\t \S]\*/')
    content = patten.sub('', content)
    file = open('tmpastfile', 'w')
    file.write(content)
    return


def generate_ast(path):
    ast_pre(path)
    content = open('tmpastfile').read()
    file = open('astfile', 'w')
    try:
        ast = parse_file('tmpastfile', use_cpp=True)
        ast.show(buf=file)
        file.close()
        file = open('astfile')
        return file.read()
    except:
        print("!!compile error!!")
        return 'error'


def process(path):
    file = open(path)
    content = file.read()
    content.replace(" ", "")
    content.replace("/n", "")
    content.replace("/t", "")
    return content.lower()


def getfingerprint(fingerprint):
    tmp = []
    for i in fingerprint:
        tmp.append(i[1])
    return tmp


def cal(fingerprinta, fingerprintb):
    ratio = len(set(fingerprinta) & set(fingerprintb))
    return float(ratio) / float(len(set(fingerprinta)))


for i in range(23):
    content1 = process("sort0.c")
    content2 = process("sort"+str(i)+".c")

    fingerprint_cl1 = getfingerprint(winnow(process_tokens('sort0.c')))
    fingerprint_cl2 = getfingerprint(winnow(process_tokens('sort'+str(i)+'.c')))

    #print winnow(process_tokens('sort0.c'))
    #print winnow(process_tokens('sort'+str(i)+'.c'))
    #print fingerprint_cl1
    #print fingerprint_cl2
    #print len(set(fingerprint_cl1) & set(fingerprint_cl2))

    fingerprint_ori1 = getfingerprint(winnow(content1))
    fingerprint_ori2 = getfingerprint(winnow(content2))

    try:
        content1 = generate_ast("sort0.c")
    except:
        pass

    try:
        content2 = generate_ast("sort"+str(i)+".c")
    except:
        pass

    fingerprint_tok1 = getfingerprint(winnow(content1))
    fingerprint_tok2 = getfingerprint(winnow(content2))

    print('data '+str(i))

    print('clang:', cal(fingerprint_cl1, fingerprint_cl2))

    print('original:', cal(fingerprint_ori1, fingerprint_ori2))

    print('ast:', cal(fingerprint_tok1, fingerprint_tok2))

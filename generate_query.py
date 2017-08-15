# Method to generate the TIGER Search query from the options selected by the user

from collections import defaultdict
import tigerAST as ast
from pprint import pprint

def getQuery(conllOutput, data):
    tokendict = defaultdict(tuple)
    for x in conllOutput[:-1]:
        temp = x.split("\t")
        tokendict[temp[0]] = (temp[1], temp[3])
    # pprint(tokendict)

    # count = 1
    # tokens = sentence.split(" ")
    # for element in tokens:
    #     tokendict[element] = count
    #     count+=1
    # pprint(tokendict)

    queryItems = defaultdict(list)
    queryItems1 = defaultdict(dict)

    for k,v in data.items():
        temp = k.split(":")
        key = temp[0]
        x = temp[1].split(" ")
        queryItems[key].append((x[0], x[1], v))

    for key,value in queryItems.items():
        reldict = defaultdict(list)
        for v in value:
            reldict[v[0]].append((v[1], v[2]))

        queryItems1[key] = reldict

# structure - dict1(dict2(list of tuples))
# eg: {'T3': { 'rel-0': [('rel', u'det'), ('dep', u'The'), ('head_label', u'NOUN')] } }

    FQ = []
    for key1, dict2 in queryItems1.items():
        token = key1
        root = []
        A = ""
        B = ""
        for key2, value2 in dict2.items():
            variable = key2.split("-")[1]
            C = ""
            D = ""
            rel = None
            for item in value2:
                if item[0] == "head":
                    A = ast.AttributeValue("word", item[1])
                if item[0] == "head_label":
                    B = ast.AttributeValue("pos", item[1])
                if item[0] == "dep":
                    # variable = str(tokendict[item[1]])
                    C = ast.AttributeValue("word", item[1])
                if item[0] == "dep_label":
                    D = ast.AttributeValue("pos", item[1])
                if item[0] == "rel":
                    rel = item[1]

            if A!="" or B!="":
                head = ast.Token(token, ast.Conjunction([A,B]))
            else:
                if rel != None:
                    head = ast.Token(token)
                else:
                    head = None
            if C!="" or D!="":
                dep = ast.Token("d"+variable, ast.Conjunction([C,D]))
            else:
                if rel != None:
                    dep = ast.Token("d"+variable)
                else:
                    dep = None
            # To avoid repeating the head values when referencing the head again and just using the token reference
            if len(root) >= 1 and head != None:
                head = ast.Token(token)
            Y = ast.DepRel(head, dep, rel)
            root.append(Y)

        if len(root) >= 2:
            if (root[0].__dict__["_rel"] == None) and (root[0].__dict__["_dep"] == None):
                root[1].__dict__["_head"] = root[0].__dict__["_head"]
                del root[0]

        FQ.append(ast.Conjunction(root))
    print "----- AST Query ---------------------------"
    print ast.Conjunction(FQ)
    print "-------------------------------------------"
    h = ast.Conjunction(FQ)
    return str(h)


# Generates the TIGER Search query from the relevant parts marked by the user
# Author: Ankita Oswal
# BA Thesis

from collections import defaultdict
import tigerAST as ast

def getQuery(data):

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
            variable = "d" + key2.split("-")[1]
            C = ""
            D = ""
            rel = None
            for item in value2:
                if item[0] == "head":
                    token = item[1].split(": ")[0]
                    A = ast.AttributeValue("word", item[1].split(": ")[1])
                if item[0] == "head_label":
                    token = item[1].split(": ")[0]
                    B = ast.AttributeValue("pos", item[1].split(": ")[1])
                if item[0] == "dep":
                    variable = item[1].split(": ")[0]
                    C = ast.AttributeValue("word", item[1].split(": ")[1])
                if item[0] == "dep_label":
                    variable = item[1].split(": ")[0]
                    D = ast.AttributeValue("pos", item[1].split(": ")[1])
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
                dep = ast.Token(variable, ast.Conjunction([C,D]))
            else:
                if rel != None:
                    dep = ast.Token(variable)
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

    h = ast.Conjunction(FQ)
    return str(h)


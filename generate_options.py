# Based on the sentence entered by the user, a list of all tokens and dependency relations is generated
# This list consists of [relation, head, head_label, dependent, dependent_label] for all relations in the dependency tree.
# Author: Ankita Oswal
# BA Thesis

import re
from collections import defaultdict

pattern1 = re.compile("^T[0-9]+.*")
pattern2 = re.compile("^R[0-9]+.*")

def getLists(annout):

    rels = []
    tags = defaultdict(list)

    TList = []
    RList = []

    for x in annout:
        if pattern1.match(x):
            TList.append(x)
        elif pattern2.match(x):
            RList.append(x)

# x has the form "R2\trelation\sArg1:T3\sArg2:T6"
# rels = [[relation,T3, T6], [...], [...]}
    for x in RList:
        R = x.split("\t")[1]
        relation = R.split(" ")
        if relation[0] == "root" or relation[0] == "ROOT":
            continue;
        temp = []
        temp.append(relation[0])
        temp.append(relation[1].split(":")[1])
        temp.append(relation[2].split(":")[1])
        rels.append(temp)

# x has the form "T3\tlabel\s3\s7\tword"
# tags = {T3: [label, word]}
    for x in TList:
        T = x.split("\t")
        key = T[0]
        label = T[1].split(" ")[0]
        word = T[2]
        tags[key].append(word)
        tags[key].append(label)

    return getOptions(rels, tags)

def getOptions(rels, tags):
    options = dict()
    finaldict = defaultdict(list)

    for idx, x in enumerate(rels):
        deprel = {}
        for kt, vt in tags.iteritems():
            if x[1] == kt:
                head = kt + ": " + vt[0]
                head_label = kt + ": " + vt[1]
                finaldict[kt] = []
                deprel["head_token"] = kt
            if x[2] == kt:
                dependent = kt + ": " + vt[0]
                dependent_label = kt + ": " + vt[1]
        deprel["rel"] = x[0]
        deprel["head"] = head
        deprel["head_label"] = head_label
        deprel["dep"] = dependent
        deprel["dep_label"] = dependent_label

        options["rel-%d" % idx] = deprel

    for key in finaldict.keys():
        for k, v in options.iteritems():
            if v["head_token"] == key:
                finaldict[key].append({k:v})

    return finaldict
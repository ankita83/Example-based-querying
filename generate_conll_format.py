# The sentence entered by the user is passed to the method getConllFormat.
# The sentence is passed as input to the SyntaxNet parser (parser.sh) which writes the conll format of the sentence into a file.
# The file is read and converted to a list that is returned to the main calling script.
# Author: Ankita Oswal
# BA Thesis

import subprocess
import os
import tempfile
import config
import json

def getConllFormat(language , sentence):

    x = unicode(sentence)
    inputFile = tempfile.NamedTemporaryFile(delete=False, dir=config.WORKING_DIRECTORY, suffix=".txt")
    outputFile = tempfile.NamedTemporaryFile(delete=False, dir=config.WORKING_DIRECTORY, suffix=".conllu")

    inputFile.write(x.encode('utf-8'))
    inputFile.close()

    ip = os.path.basename(inputFile.name)
    op = os.path.basename(outputFile.name)

    # run bash commands from this script using subprocess
    command = '''
        MODEL_DIRECTORY="%s/%s"
        cat %s | %s $MODEL_DIRECTORY > %s
        ''' % (config.MODEL_DIRECTORY,language,ip, config.PARSER_PATH, op)

    process = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True,
                               cwd= config.WORKING_DIRECTORY)
    process.communicate(command)

    # read outputFile and write it to a list
    output = []
    for line in outputFile:
        output.append(line)

    outputFile.close()

    # delete all files created in the process
    os.remove(inputFile.name)
    os.remove(outputFile.name)

    # return the list containing the conll format of the user enetered sentence
    return output

# Method called when user selects parts of the sentence relevant for query generation.
# The input example and marked parts are passed to Tundra in order to mark the selections in the dependency tree.
def getSelectedList(language, conllOutput, query):

    fq = "\"" + query.replace('"', '\\"') + "\""
    with open('temp.conllu', 'w') as f:
        for x in conllOutput:
            f.write(x)

    command = '''
            CONLLU2_FILE=temp.conllu
            QUERY=%s
            LANGUAGE=%s
            API="https://weblicht.sfs.uni-tuebingen.de/tundra-beta/api/query/visres"
            curl -X POST -F "file=@$CONLLU2_FILE" -F "query=$QUERY" -F "lang=$LANGUAGE" "$API" > api-test.json
            ''' % (fq, language)

    process = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    process.communicate(command)

    with open("api-test.json") as dataFile:
        data = json.load(dataFile)
        selectedWord = []
        selectedRel = []
        nodes = set()
        relations = set()

        allNodes = {}
        allRels = {}

        for item in data:
            for x in item["d3Input"]["queryMatch"]:
                nodes.add(x["terminalPosition"])
            for y in item["d3Input"]["queryRelations"]:
                relations.add(y["id"])

        for item in data[0]["d3Input"]["nodes"]:
            key = item["node"].split("n")[1]
            value = item["name"]
            allNodes[key] = value
        for item in data[0]["d3Input"]["links"]:
            key = item["id"]
            value = item["dependency"]
            allRels[key] = value

        for k, v in allNodes.items():
            for x in nodes:
                if int(k) == x:
                    selectedWord.append(v)

        for k, v in allRels.items():
            for x in relations:
                if x == k:
                    selectedRel.append(v)
    os.remove("temp.conllu")
    os.remove("api-test.json")

    return [selectedWord, selectedRel]




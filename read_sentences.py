# main script.
# user enters a sentence (index.html)
# selected sentence is then passed to the necessary scripts in order to finally view the dependency tree.
# and the tokens that the user can select in order to create a search query (in TIGERSearch format)

import web
import conll_to_standoff
import bratObject
import generate_options
import generate_conll_format
import config
import string
import generate_query
import webbrowser as wb
import urllib as ul
from pprint import pprint

urls = ('/', 'index','/showSentence','showSentence','/displayOptions','displayOptions', '/displaySearch', 'displaySearch')
app = web.application(urls, globals())
web.config.debug = True

if not web.config.get('session'):
    session = web.session.Session(app,
        web.session.DiskStore('./sessions'),
        initializer={'language':"", 'sentence':"", 'finalQuery':"", 'conllOutput':"", 'bratformat':""}
    )
    web.config.session = session
else:
    session = web.config.session

# Controller
class index:
    def __init__(self):
        self.render = web.template.render('templates/')

    def GET(self, name=None):
        return self.render.index(config.language_to_model)

class showSentence:
    def __init__(self):
        self.render = web.template.render('templates/')

    def POST(self):
        showSentence.set_sent(web.input().values())
        data = showSentence.process_sent(self)
        return self.render.showSentence(data)

# process the sentence entered by the user: check punctuation errors, convert to conll format.
# Convert conll to standoff format for bratnlp.
# generate the necessary objects to view the dependency tree and the options that the user can select
    @classmethod
    def set_sent(self,sent):
        session['language'] = sent[0]

        # check if there is a space before last punctuation character, if not insert one
        x = sent[1]
        if x[-1] in string.punctuation:
            if x[len(x)-1] != " ":
                temp = x[:-1] + " " + x[-1]
                sent[1] = temp

        session['sentence'] = sent[1]

    def process_sent(self):
        session['conllOutput'] = generate_conll_format.getConllFormat(session['language'], session['sentence'])
        session['bratformat'] = conll_to_standoff.process(session['conllOutput'][:-1])
        options = generate_options.getLists(session['bratformat'])
        bratObjects = bratObject.createBratObjects(session['bratformat'],[], [])
        return [bratObjects, options]

# Processes the options selected by the user to generate the search query
# and then view the search results
class displayOptions:
    def __init__(self):
        self.render = web.template.render('templates/')

    def POST(self):
        data = web.input()
        bratObjects = displayOptions.display_query(data)
        return self.render.displayOptions(bratObjects, session['finalQuery'])

    @classmethod
    def display_query(self, options):
        session['finalQuery'] = generate_query.getQuery(session['conllOutput'], options)
        tempList = generate_conll_format.getSelectedList(session['language'], session['conllOutput'], session['finalQuery'])
        bratObjects = bratObject.createBratObjects(session['bratformat'], tempList[0], tempList[1])
        return bratObjects

class displaySearch:
    def __init__(self):
        self.render = web.template.render('templates/')

    def POST(self):
        treebank = config.language_to_model[session['language']]
        q = ul.quote(session['finalQuery'].encode('utf-8'))
        wb.open("https://weblicht.sfs.uni-tuebingen.de/tundra-beta/public/treebank.html?bank=%s&q=%s" % (treebank, q))
        return self.render.displaySearch()

if __name__ ==\
        '__main__':
    app.run()

#--------------------------------------------------------
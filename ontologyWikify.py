import sys, http.client, urllib.request, urllib.parse, urllib.error, json
import re
import nltk
from nltk import tokenize, word_tokenize, sent_tokenize

from pprint import pprint

class ontology:
    def __init__(self,subject):
        self.subject = subject
        self.devs = construct(subject)

def getUrl( domain, url ) :
    # Headers are used if you need authentication
    headers = {}
    # If you know something might fail - ALWAYS place it in a try ... except
    try:
        conn = http.client.HTTPSConnection( domain )
        conn.request("GET", url, "", headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        return data 
    except Exception as e:
        # These are standard elements in every error.
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
    # Failed to get data!
    return None
def quickTitles(subject):
    query = urllib.parse.quote_plus(subject)
    urlData = getUrl('en.wikipedia.org', '/w/api.php?action=query&list=search&format=json&srsearch='+query)
    urlData = json.loads(urlData.decode("utf-8"))
    titles = []
    for i in urlData["query"]["search"]:
        titles.append(i['title'].lower())
    pprint(titles)
#Hand-made ontology
'''def construct(subject):
    if subject == "Science":
        derivatives = []
        for item in ["computer science","social science","political science","forensic science","robotics"]:
            derivatives.append(ontology(item))
        return derivatives
    else:
        return None'''

#The subjects we will construct
subs = ["robotics"]
#All the subjects that have already been created
allSubs = []
#Words to be eliminated from titles
elimWords = ["theoretical","bachelor","master","of","and","in","for","college","faculty","outline","list"]
elimWords = elimWords+["glossary","[(]","fiction","conferences","history","fiction","conferences","history"]
elimWords = elimWords+["doctor"]
def construct(subject):
    allSubs.append(subject)
    query = urllib.parse.quote_plus(subject)
    urlData = getUrl('en.wikipedia.org', '/w/api.php?action=query&list=search&format=json&srsearch='+query)
    if urlData is not None:
        titles = []
        urlData = json.loads(urlData.decode("utf-8"))
        for i in urlData["query"]["search"]:
            title = i['title'].lower()
            title = title.replace("'","")   #Remove apostrophes and brackets
            title = title.replace("(","")
            title = title.replace(")","")
            nTitle = []
            for word in word_tokenize(title):   #Remove superfluous words
                if word not in elimWords:
                    nTitle.append(word)
            title = " ".join(nTitle)    #Join the remaining title back together
            print(title)
            goodTitle = True
            if title not in titles and title not in allSubs: #No duplicates and no previous subjects
                if urllib.parse.quote_plus(title) and not re.match("^"+subject+"$",title,re.IGNORECASE):
                    #Does not include the subject itself
                    titles.append(title)
        derivatives = []
        pprint(titles)
        for title in titles:
            derivatives.append(ontology(title))
        return derivatives
    else:
        return None

'''# This makes sure that any funny charecters (including spaces) in the query are
# modified to a format that url's accept.
query = urllib.parse.quote_plus( query )

# Call our function.
url_data = get_url( 'en.wikipedia.org', '/w/api.php?action=query&list=search&format=json&srsearch=' + query )

# We know how our function fails - graceful exit if we have failed.
if url_data is None :
print( "Failed to get data ... Can not proceed." )
# Graceful exit.
sys.exit()

# http.client socket returns bytes - we convert this to utf-8
url_data = url_data.decode( "utf-8" ) 

# Convert the structured json string into a python variable 
url_data = json.loads( url_data )

# Pretty print
pprint( url_data )

# Now we extract just the titles
titles = [ i['title'] for i in url_data['query']['search'] ]
pprint( titles )

# Make sure we can plug these into urls:
url_titles = [ urllib.parse.quote_plus(i) for i in titles ]
pprint( url_titles )'''

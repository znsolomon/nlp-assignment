import nltk
import pickle
import re
from os import listdir
from os.path import isfile, join
from nltk.tag import UnigramTagger
from nltk import tokenize, word_tokenize, sent_tokenize

#Load the email
test = open("302.txt", "r")
email = test.read()
test.close()

#Separate the header from the main body using regex
sep = re.search(r'Abstract:',email)
if sep:
    header = email[:225]    #Separate the header from the body
    body = email[235:]

#Extract useful information from the header
lecType = re.search('(Type:\s*)\w*.*',header)           #Finds the lecture type
lecTopic = re.search('(Topic:\s*)\w*.*',header)         #Finds the lecture topic
lecDates = re.search('(Dates\s*)\w*.*',header)          #Finds the lecture dates
lecTime = re.search('(Time:\s*)\w*.*',header)           #Finds the lecture times
lecPostedBy = re.search('(PostedBy:\s*)\w*.*',header)   #Finds who posted the message
#Each of these is found by finding the appropriate title,
#and finding the string of words afterwards until a newline is reached
headerInfo = {'Type':lecType,'Topic':lecTopic,'Dates':lecDates,'Time':lecTime,'PostedBy':lecPostedBy}
print(headerInfo)

#Load the trained POS tagger
pos = pickle.load(open("tagfile","rb"))

#POS tag the email using the tagger
tagEmail =[]
for sent in sent_tokenize(body):
    tagEmail.append(pos.tag(word_tokenize(sent)))

#Extract proper nouns from the email using regex
propNouns = []
#Find all capitalised words that are not directly after a full stop.
propNouns = re.findall('(?<=[^.]\s)[A-Z]\w+',body)
if propNouns:
    print(propNouns)

#Write the email to a new file
output = open("302Out.txt","w")
for sent in tagEmail:
    for word in sent:
        if word[1] == None:
            tag = 'None'
        else:
            tag = word[1]
        output.write("<"+tag+">"+word[0]+"</"+tag+"> ")
    output.write("\n")
output.close()


#STARTING REGEX FOR PROPNOUN EXTRACTION: (?<=[^.]\s)[A-Z]\w+

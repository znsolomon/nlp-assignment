import nltk
import pickle
import re
from os import listdir
from os.path import isfile, join
from nltk.tag import UnigramTagger
from nltk import tokenize, word_tokenize, sent_tokenize

#Load the email
test = open("testEmail.txt", "r")
email = test.read()
test.close()

#Load the trained POS tagger
pos = pickle.load(open("tagfile","rb"))

#POS tag the email using the tagger
tagEmail =[]
for sent in sent_tokenize(email):
    tagEmail.append(pos.tag(word_tokenize(sent)))

#Extract proper nouns using regex
propNouns = re.findall( r'(?!.)\s[A-Z]',email)

#Extraction method not using regex: crude
for sent in tagEmail:
    for i in range(1,len(sent)):
        word = sent[i]
        if word[0][0].isupper():
            print(word)

#Write the email to a new file
output = open("testOutput.txt","w")
for sent in tagEmail:
    for word in sent:
        if word[1] == None:
            tag = 'None'
        else:
            tag = word[1]
        output.write("<"+tag+">"+word[0]+"</"+tag+"> ")
    output.write("\n")
output.close()

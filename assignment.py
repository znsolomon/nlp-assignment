import nltk
import pickle
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

#Process the email using the tagger
tagEmail =[]
for sent in sent_tokenize(email):
    tagEmail.append(pos.tag(word_tokenize(sent)))
    
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

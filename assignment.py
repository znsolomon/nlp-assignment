import nltk
import pickle
import re
import os
from os import listdir
from os.path import isfile, join
from nltk.tag import UnigramTagger
from nltk import tokenize, word_tokenize, sent_tokenize
import name_tagger

def insertString(string,index,insert):
    return string[:index]+insert+string[index:]

def findSublist(data,item):     #Given a list of lists and an item, returns the list that contains the item
    for sublist in data:
        if item in sublist:
            return sublist
    return None

for file in os.listdir("/home/students/zns733/work/NLP/nlp-assignment-master/seminar_testdata/test_untagged"):
    #file = "402.txt"       #For selecting specific files
    print (file)
    #Load the email
    test = open("/home/students/zns733/work/NLP/nlp-assignment-master/seminar_testdata/test_untagged/"+file, "r")
    email = test.read()
    test.close()

    #Separate the header from the main body using regex
    sep = re.search(r'Abstract:',email)
    if sep:
        header = email[:sep.start()]    #Separate the header from the body
        body = email[sep.end():]

    #Extract useful information from the header
    lecType = re.search('(Type:\s*)(\w*.)*',header)           #Finds the lecture type
    lecTopic = re.search('(Topic:\s*)(\w*.)*',header)         #Finds the lecture topic
    lecDates = re.search('(Dates:\s*)(\w*.)*',header)          #Finds the lecture dates
    lecTime = re.search('(Time:\s*)(\w*.)*',header)           #Finds the lecture times
    lecPostedBy = re.search('(PostedBy:\s*)(\w*.)*',header)   #Finds who posted the message
    lecPlace = re.search('(Place:\s*)(\w*.)*',header)           #Finds the lecture location
    lecWho = re.search('(Who:\s*)(\w*.)*',header)               #Finds the speaker
    #Each of these is found by finding the appropriate title,
    #and finding the string of words afterwards until a newline is reached
    
    #Extract date
    foundDate = True
    foundPostDate = True
    dateRegs = ['\d\d[^.\w]\w\w\w[^.\w]\d\d','\d[^.\w]\w\w\w[^.\w]\d\d','\d\d[^.\w]\w\w\w[^.\w]\d']
    for reg in dateRegs:
        date = re.search(reg,lecDates.group(0))
        if date:
            break
    if not date:
        foundDate = False
        
    for reg in dateRegs:
        postDate = re.search(reg,lecPostedBy.group(0))
        if postDate:
            break
    if not postDate:
        foundPostDate = False
        
    #Extract time, including allowing for multiple times
    timeRegs = ['\d*:\d*\sam','\d*:\d*\spm','\d*:\d\d*']
    times = []
    foundTime = True
    eFoundTime = True
    for reg in timeRegs:
        tCheck = re.findall(reg,lecTime.group(0),re.IGNORECASE)
        for match in times:
            tPrev = re.search(reg,match,re.IGNORECASE)
            if tPrev:
                for time in tCheck:
                    if tPrev.group(0) == time:
                        #Ignores multiple matches of the same time
                        tCheck.remove(time)
                        break
        if len(tCheck) > 0:
            for item in tCheck:
                times.append(item)
    if (times == []):
        foundTime = False
    else:
        sTime = times[0]
        if len(times) > 1:
            eTime = times[1]
        else:
            eFoundTime = False

    #Load the trained POS tagger
    pos = pickle.load(open("tagfile","rb"))

    #POS tag the body using the tagger
    namesTagger = name_tagger.NamesTagger()
    uTagEmail = []  #Tokenized email ready to be tagged
    tagEmail =[]    #The complete tagged email
    for sent in sent_tokenize(body):
        uTagEmail.append(word_tokenize(sent))
    for sent in uTagEmail:
        tagSent = pos.tag(sent)
        tagSentFinal = []
        for word in tagSent:
            if namesTagger.choose_tag(word[0],None) == 'NNP':
                tagSentFinal.append((word[0],'NNP'))
            else:
                tagSentFinal.append(word)
        tagEmail.append(tagSentFinal)

    #Extract proper nouns from the email using regex
    #Find all capitalised words that are not directly after a full stop.
    propNouns = re.findall('(?<=[^.]\s)[0-Z]\w+',body)

    #Attempt to extract speaker name using the header. If not, use the tags
    foundName = False
    if lecWho:
        names = []
        for word in word_tokenize(lecWho.group(0)):
            if namesTagger.choose_tag(word,None) == 'NNP':
                names.append(word)
        if names != []:
            foundName = True
            speaker = ""
            for word in names:
                speaker = speaker+word+" "
            speaker = speaker[:len(speaker)-1]      #Remove the last whitespace
    #Multiple if statements used to find the correct way to extract the speaker name
    if not foundName:  #If nothing can be found from the header, extract name from body
        bodyCheck = re.search('(?<=(Visitor)|(Speaker)):\s*(\w*.)*',body,re.IGNORECASE)
        if bodyCheck:
            speakerList = word_tokenize(bodyCheck.group(0))
            speaker = ""
            for word in speakerList:
                speaker = speaker+word+" "
            speaker = speaker[2:len(speaker)-1]      #Remove the last whitespace and colon at start
            foundName = True
    if not foundName:
        potNames = []
        for sent in tagEmail:
            for word in sent:
                if word[1] == 'NNP' and word[0] in propNouns:
                    potNames.append(word)
        print(potNames)
        if len(potNames) == 1:  #Only one name remaining
            name = potNames[0]
            speaker = name[0] + " "
            sent = findSublist(tagEmail,name)
            wordCount = 1
            while True:
                if sent[sent.index(name)+wordCount][1] == None: #Words after have no tags, are also names
                    speaker = speaker + sent[sent.index(name)+wordCount][0] + " "
                    wordCount += 1
                else:
                    speaker = speaker[:len(speaker)-1]  #Remove the last whitespace
                    foundName = True
                    break 
    print(speaker)
    #Tag the email with the information extracted
    if foundDate:
        dates = re.finditer(date.group(0),email)
        charTrack = 0
        for item in dates:
            email = insertString(email,item.start()+charTrack,"<date>")
            charTrack += 6
            email = insertString(email,item.end()+charTrack,"</date>")
            charTrack += 7            
    if foundPostDate:
        postDates = re.finditer(postDate.group(0),email)
        charTrack = 0
        for item in postDates:
            email = insertString(email,item.start()+charTrack,"<postdate>")
            charTrack += 10
            email = insertString(email,item.end()+charTrack,"</postdate>")
            charTrack += 11
    if foundTime:
        sTimes = re.finditer(sTime,email,re.IGNORECASE)
        charTrack = 0
        for item in sTimes:
            email = insertString(email,item.start()+charTrack,"<sTime>")
            charTrack += 7
            email = insertString(email,item.end()+charTrack,"</sTime>")
            charTrack += 8
    if eFoundTime:
        eTimes = re.finditer(eTime,email,re.IGNORECASE)
        charTrack = 0
        for item in eTimes:
            email = insertString(email,item.start()+charTrack,"<eTime>")
            charTrack += 7
            email = insertString(email,item.end()+charTrack,"</eTime>")
            charTrack += 8

    #Write the email to a new file
    output = open("/home/students/zns733/work/NLP/nlp-assignment-master/seminar_testdata/test_untagged_output/"+insertString(file,3,"out"),"w")
    output.write(email)
    output.close()

    break                      #If only one file needs to be tested
'''    output = open("302Out.txt","w")
    for sent in tagEmail:
        for word in sent:
            if word[1] == None:
                tag = 'None'
            else:
                tag = word[1]
            output.write("<"+tag+">"+word[0]+"</"+tag+"> ")
        output.write("\n")
    output.close()'''

#STARTING REGEX FOR PROPNOUN EXTRACTION: (?<=[^.]\s)[0-Z]\w+

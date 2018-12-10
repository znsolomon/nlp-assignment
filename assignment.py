import nltk
import pickle
import re
import os
from os import listdir
from os.path import isfile, join
from nltk.tag import UnigramTagger
from nltk import tokenize, word_tokenize, sent_tokenize
from nltk.corpus import semcor
from nltk.corpus import wordnet as wn
import name_tagger
import ontologyConstruction

def insertString(string,index,insert):
    return string[:index]+insert+string[index:]

def findSublist(data,item):     #Given a list of lists and an item, returns the list that contains the item
    for sublist in data:
        if item in sublist:
            return sublist
    return None

def readCorpus(file,item):
    data = open(file,"r")
    text = data.read()
    corpus = word_tokenize(text.lower())
    definition = word_tokenize(item.lower())
    for word in corpus:
        for dWord in definition:
            if dWord == word:
                return True
    return False

#Load ontology to use later
ontology = pickle.load(open("academicOntology","rb"))

#Function that searches for the subject
def findSub(ontology,text,level):
    subjects = []
    inText = re.findall(ontology.subject+"(?=[^A-z])",text,re.IGNORECASE)   #Only finds whole words
    subject = ontology.subject
    trueSubject = subject
    hits = len(inText)
    trueHits = hits
    if ontology.devs == []:
        if inText == []: #Return the subject if no derivatives exist
            return None
        else:
            return [subject,hits,level]
    else:
        for dev in ontology.devs:
            hits = trueHits
            subject = trueSubject
            if findSub(dev,text,level) != None:
                subject = subject+"/"+str(findSub(dev,text,level)[0])
                #Will always choose the subject farthest down the ontology
                hits = hits + findSub(dev,text,level)[1]  #Hits are cummulative
                subjects.append([subject,hits,level+1])
        if subjects == []:#If no derivatives get hits, add the last hit to subjects
            if inText != []:
                subjects.append([subject,hits,level])
            else:
                return None
        chosen = None
        if len(subjects) == 1:
            chosen = subjects[0]
        #Decide on the best subject based on the hits each generated
        elif len(subjects) > 1:
            mostHits = 0
            for sub in subjects:
                if sub[1] > mostHits:
                    chosen = sub
                    mostHits = sub[1]
        return chosen

nameRecall = 0
locRecall = 0
timeRecall = 0

directory = os.getcwd()
for file in os.listdir(directory + "/seminar_testdata/test_untagged"):
    #file = "443.txt"       #For selecting specific files
    #Load the email
    data = open(directory+"/seminar_testdata/test_untagged/"+file, "r")
    email = data.read()
    data.close()

    #Separate the header from the main body using regex
    sep = re.search('Abstract:',email)
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
    lecHost = re.search('(Host:\s*)(\w*.)*',header)             #Finds the host
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
    #timeRegs = ['\d*:\d*\sam','\d*:\d*\spm','\d*:\d\d*']
    timeRegs = "(\d{1,2}[^0-9]\d{1,2} *p*[.]*m*[.]*)|(\d+ *p[.]*m[.]*)"
    times = []
    foundTime = True
    eFoundTime = True
    tCheck = re.findall(timeRegs,lecTime.group(0),re.IGNORECASE)
    for item in tCheck:
        times.append(item[0])
    if (times == []):
        foundTime = False
        eFoundTime = False
    else:
        sTime = times[0]
        if len(times) > 1:
            eTime = times[1]
        else:
            eFoundTime = False
            
    #Load the trained POS tagger
    pos = pickle.load(open("tagfile","rb"))

    #POS tag the body using the tagger
    bodySents = sent_tokenize(body)
    namesTagger = name_tagger.NamesTagger()
    uTagEmail = []  #Tokenized email ready to be tagged
    tagEmail =[]    #The complete tagged email
    for sent in bodySents:
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
    #First, reduce tagEmail into a single-dimensional array
    tagEmail1d = []
    for sent in tagEmail:
        for word in sent:
            tagEmail1d.append(word)

    #Extract proper nouns from the email using regex
    #Find all capitalised words that are not directly after a full stop. (Firstly extract the 'Doctor' proper nouns
    propNouns = re.findall('(?<=[Dr.]\s)[0-Z]\w+',body)
    propNouns = propNouns + re.findall('(?<=[^.]\s)[0-Z]\w+',body)

    #Attempt to extract host name using the header
    foundHost = False
    if lecHost:
        hNames = []
        for word in word_tokenize(lecHost.group(0)):
            if namesTagger.choose_tag(word,None) == 'NNP':
                hNames.append(word)
        
    #Attempt to extract speaker name using the header. If not, use the tags
    foundName = False
    nameHeader = False
    if lecWho:
        names = []
        for word in word_tokenize(lecWho.group(0)):
            if namesTagger.choose_tag(word,None) == 'NNP':
                names.append(word)
        if names != []:
            foundName = True
            nameHeader = True
            speaker = ""
            namesTagged = []
            sent = pos.tag(word_tokenize(lecWho.group(0)))
            for item in sent:
                word = item[0]
                if word in names:
                    namesTagged.append(item)
            lastWord = namesTagged[-1]
            wordCount = 1
            while True:
                try:
                    nextTag = sent[sent.index(lastWord)+wordCount][1]
                    if nextTag == 'NNP' or nextTag == None:
                        names.append(sent[sent.index(lastWord)+wordCount][0])
                        wordCount += 1
                    else:
                        break
                except IndexError:  #If the end of the line is reached
                    break
            for word in names:
                speaker = speaker+word+" "
            speaker = speaker[:len(speaker)-1]      #Remove the last whitespace
      
    #Multiple if statements used to find the correct way to extract the speaker name
    if not foundName:  #If nothing can be found from the header, extract name from body
        bodyCheck = re.search('(?<=(Visitor)|(Speaker)):\s*(\w*\s)*',body,re.IGNORECASE)
        if bodyCheck:
            speakerList = word_tokenize(bodyCheck.group(0))
            speaker = ""
            for word in speakerList:
                speaker = speaker+word+" "
            speaker = speaker[2:len(speaker)]      #Remove the last whitespace and colon at start
            foundName = True
            for item in tagEmail1d:
                if item[0] == speakerList[-1]:
                    lastName = item
                    break
            
    if not foundName:       #If no obvious clues are in the text, look at tagging and word senses
        potNames = []
        for word in tagEmail1d:
            if word[1] == 'NNP' and word[0] in propNouns:
                potNames.append(word)
        if len(potNames) == 0:   #potNames is empty, so take non-name words
            for word in tagEmail1d:
                if word[1] == None and word[0] in propNouns:
                    potNames.append(word)
        nPotNames = []  #Now all the incorrect items in potNames must be removed
        #Remove duplicates
        seen = set()
        for item in potNames:
            if item not in seen:
                nPotNames.append(item)
                seen.add(item)
        potNames = nPotNames
        nPotNames = []  #Remove non-name words
        for item in potNames:
            senses = wn.synsets(item[0])
            if len(senses) == 0:        #Words with no definitions are names
                nPotNames.append(item)
            else:
                for sense in senses:#Check the definition of the word for key identifiers of names:
                    if readCorpus(directory+"/gazetteers/nationalities.txt",sense.definition()):
                        nPotNames.append(item)  #Nationalities
                        break
                    elif readCorpus(directory+"/professions.txt",sense.definition()):
                        nPotNames.append(item)  #Profession titles
                        break
        potNames = nPotNames
        #Now the correct names need to be identified
        nPotNames = []
        #Eliminate any acronyms (all capitals) or numbers (all numbers)
        for name in potNames:
            if not (re.search('\d*',name[0]).group(0) == name[0]) and not (re.search('[A-Z]*',name[0]).group(0) == name[0]):
                if lecHost:     #The host and speaker are different people
                    isHost = False
                    for hName in hNames:
                        if name[0] == hName:
                            isHost = True
                    if not isHost:
                        nPotNames.append(name)
                else:
                    nPotNames.append(name)
                    
        potNames = nPotNames
        #potNames has been reduced: now to construct speaker
        speaker = ""
        lastName = ""
        if len(potNames) == 1:  #Only one name remaining
            name = potNames[0]
            speaker = name[0] + " "
            lastName = name
            foundName = True
        elif len(potNames) > 1:
            oneName = True      #If more than one name remains, make sure they are next to each other (the same name)
            for i in range(len(potNames)-1):
                word = potNames[i]
                nextWord = potNames[i+1]
                if tagEmail1d.index(word) != tagEmail1d.index(nextWord)-1:
                    oneName = False
                    break
            if oneName:
                for item in potNames:
                    name = item[0]
                    speaker = speaker + name + " "
                lastName = potNames[-1]
                foundName = True
    #Now pick up any names that were not in the 'names' corpus
    if foundName and not nameHeader:
        sent = findSublist(tagEmail,lastName)
        wordCount = 1
        while True:
            try:
                nextTag = sent[sent.index(lastName)+wordCount][1]
                if nextTag == None or nextTag == 'NNP':
                    #Words after that have no tags are also names
                    speaker = speaker + sent[sent.index(lastName)+wordCount][0] + " "
                    wordCount += 1
                else:
                    speaker = speaker[:len(speaker)-1]  #Remove the last whitespace
                    break
            except IndexError:  #If name is at the end of a sentence
                speaker = speaker[:len(speaker)-1]  #Remove the last whitespace
                break      

    #Find location using header
    foundLocation = False
    locRegs = ["([\dA-Z]+ *wean hall)","(wean hall *[\dA-Z]+)","(baker hall)","(\d* *doherty hall *\d*)","mellon institute building","([\dA-Z]+ *weh)","(weh *[\dA-Z]+)","([\dA-Z]+ *wean)","(wean *[\dA-Z]+)","\d\w\w floor conference room","sei auditorium","porter hall [\dA-Z]*","pittsburgh supercomputing center","\d* cathedral of learning","(\d* *doherty *\d*)"]
#Above is the regex for all locations found in the 'place' tab of all emails used for testing.
    if lecPlace:
        for reg in locRegs:
            location = re.search(reg,lecPlace.group(0),re.IGNORECASE)
            if location:
                foundLocation = True
                break
    else:   #Search the body for locations shown above
        for reg in locRegs:
            location = re.search(reg,body,re.IGNORECASE)
            if location:
                foundLocation = True
                break
    #Tag the email with the information extracted
    #Find and tag sentences
    sentMarkers = re.finditer('[\n.!?]\W(?=[A-Z])',body)
    sentMarkList = re.findall('[\n.!?]\W(?=[A-Z])',body)
    charTrack = 0
    headLen = len(header)+9
    markCount = 0
    for mark in sentMarkers:
        if markCount == 0:
            email = insertString(email,mark.end()+headLen+charTrack,"<sentence>")
            charTrack += 10
        else:
            email = insertString(email,mark.start()+headLen+charTrack,"</sentence>")
            charTrack += 11
            email = insertString(email,mark.end()+headLen+charTrack,"<sentence>")
            charTrack += 10
        if markCount == len(sentMarkList)-1:
            email = insertString(email,len(email)-1,"</sentence>")
            charTrack += 11
        markCount += 1
    #Find and tag paragraphs
    parMarkers = re.finditer('\n\n',email)
    parMarkersList = re.findall('\n\n',email)
    charTrack = 0
    headLen = len(header)+9
    markCount = 0
    for mark in parMarkers:
        if mark.start() > headLen:  #Only marks sentences in the body
            if markCount == 0:
                email = insertString(email,mark.end()+charTrack,"<paragraph>")
                charTrack += 11
            else:
                email = insertString(email,mark.start()+charTrack,"</paragraph>")
                charTrack += 12
                email = insertString(email,mark.end()+charTrack,"<paragraph>")
                charTrack += 11
            if markCount == len(parMarkersList)-1:
                email = insertString(email,len(email),"</paragraph>")
                charTrack += 12
        markCount += 1
    #Tag information
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
            email = insertString(email,item.start()+charTrack,"<stime>")
            charTrack += 7
            email = insertString(email,item.end()+charTrack,"</stime>")
            charTrack += 8
        timeRecall += 1
    if eFoundTime:
        eTimes = re.finditer(eTime,email,re.IGNORECASE)
        charTrack = 0
        for item in eTimes:
            email = insertString(email,item.start()+charTrack,"<etime>")
            charTrack += 7
            email = insertString(email,item.end()+charTrack,"</etime>")
            charTrack += 8
    if foundName:
        names = re.finditer(speaker,email,re.IGNORECASE)
        charTrack = 0
        for item in names:
            email = insertString(email,item.start()+charTrack,"<speaker>")
            charTrack += 9
            email = insertString(email,item.end()+charTrack,"</speaker>")
            charTrack += 10
        nameRecall += 1
    if foundLocation:
        locations = re.finditer(location.group(0),email,re.IGNORECASE)
        charTrack = 0
        for item in locations:
            email = insertString(email,item.start()+charTrack,"<location>")
            charTrack += 10
            email = insertString(email,item.end()+charTrack,"</location>")
            charTrack += 11
        locRecall += 1

    #Find the correct subject in the ontology
    subject = None
    if lecType:
        subject = findSub(ontology,lecType.group(0),0) #Check the header first, it's more likely to be there
    if subject == None:
        subject = findSub(ontology,email,0)   #Only check the full email if the header is not there
    #Adds the subject to the front of the email
    if subject == None:
        email = "SUBJECT: "+str(subject)+"\n---------------------------------\n"+email
    else:
        email = "SUBJECT: "+str(subject[0])+"\n---------------------------------\n"+email

    print(file)
    print(subject)
    #Write the email to a new file
    output = open(directory+"/seminar_testdata/test_untagged_output/"+insertString(file,3,"out"),"w")
    output.write(email)
    output.close()

    #break                      #If only one file needs to be tested
stats = [timeRecall,timeRecall/185,nameRecall,nameRecall/185,locRecall,locRecall/185]
#print(stats)

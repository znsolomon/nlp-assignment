import re
import os
import pickle

class ontology:
    def __init__(self,subject,subtext,tag):
        self.subject = subject
        self.devs = construct(subtext,tag)

def checkTag(text,tag): #Returns the index value of a tag in text, or none
    index = 0
    live = ""
    while index < len(text):
        live = live + text[index]
        if live == tag:
            return index
        elif live not in tag:
            live = ""
        index += 1
    return None
        
def construct(text,tag):
    subtext = ""
    subject = ""
    nextTag = ""
    if tag == "":
        return []
    elif tag[0] == "h":   #Finds where the subject is in the text
        finder = "id"
    else:
        finder = "title"
    #Sets up tag for next iteration
    if tag == "h2":
        nextTag = "h3"
    else:
        nextTag == "li"
    htmlSearch = re.finditer('(<'+tag+'><(\S+ +)+'+finder+'=")([A-z]+[ \-&]*)+',text,re.IGNORECASE)
    headers = []
    badHeaders = [] #Headers that have already been added in a different place
    devs = []
    for obj in htmlSearch:
        headers.append(obj)
    for i in range(0,len(headers)):
        header = headers[i]
        if i not in badHeaders:
            if i == len(headers)-1:
                subtext = text[header.end():]
            else:
                subtext = text[header.end():headers[i+1].start()]
            if tag == "li":
                if checkTag(subtext,"<ul>") != None:
                    #Search for <ul> tags that indicate indents
                    startIndent = checkTag(subtext,"<ul>")
                    endIndents = re.finditer("</ul>",text[startIndent:])
                    endIndent = None
                    indentsList = []
                    for item in endIndents:
                        indentsList.append(item)
                    #If there are multiple tags, take the first one
                    endIndent = indentsList[0].end()
                    endIndent += len(text[:startIndent])
                    subtext = text[len(text[:header.end()])+startIndent:endIndent]
                    nextTag = "li"
                    #Flag the lines as already being added
                    indentLines = re.findall("<li>",subtext)
                    j = 1
                    for line in indentLines:
                        badHeaders.append(i+j)
                        j += 1
                else:
                    nextTag == ""
            elif tag == "h3":
                h4Search = re.search('<h4>',subtext)
                if h4Search:
                    nextTag = "h4"
                else:
                    nextTag = "li"
            subject = re.search('(?<='+finder+'=")([A-z\-\(\)]+ *)+',header.group(0)).group(0)
            #Properly format the subject
            subject = subject.replace("_"," ")
            devs.append(ontology(subject,subtext,nextTag))
    return devs

def displayOnt(ontology,layer):
    output = layer + ontology.subject + "\n"
    for dev in ontology.devs:
        output = output + displayOnt(dev,layer+"-") +"\n"
    return output

directory = os.getcwd()
data = open(directory+"/departmentOntology.txt","r")
html = data.read()
data.close()

academia = ontology("Academic fields ontology",html,"h2")
fileName = "academicOntology"
fileObj = open(fileName,"wb")
pickle.dump(academia,fileObj)
fileObj.close()

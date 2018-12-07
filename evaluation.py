import os
import re
from os import listdir

def insertString(string,index,insert):
    return string[:index]+insert+string[index:]

class tagStats():   #Tracks all the stats of a particular tag in a particular email
    def __init__(self,tag,correct,missing,target,actual):
        self.tag = tag
        self.correct = correct
        self.missing = missing
        self.target = target
        self.actual = actual

def present(stats): #Presents a specific email's stats
    output = ""
    for stat in stats:
        output = output + stat.tag+": "+str(stat.correct) +"\n"
        if stat.missing:
            output = output + "No tags found in email. Target tags:" + "\n"
            output = output + str(stat.target) + "\n"
        elif not stat.correct:
            output = output + "Target tags:" + "\n"
            output = output + str(stat.target) + "\n"
            output = output + "Actual tags:" + "\n"
            output = output + str(stat.actual) + "\n"
    return output

class trackTotals():    #Keeps the running totals of all tags
    def __init__(self,tag): #No true negatives exist, as all the emails are tagged
        self.tag = tag
        self.truePos = 0
        self.falsePos = 0
        self.falseNeg = 0
    def incTP(self):
        self.truePos += 1
    def incFP(self):
        self.falsePos += 1
    def incFN(self):
        self.falseNeg += 1
    def presentStats(self):
        recall = (self.truePos)/(self.truePos+self.falseNeg)
        precision = self.truePos / (self.falsePos + self.truePos)
        return "TOTAL STATS\n"+self.tag +"\nRecall: "+str(recall)+"\nPrecision: "+str(precision)+"\n"

directory = os.getcwd()
evalDoc = ""    #The final document evaluation
tags = ["speaker","stime","location","paragraph","sentence"]
totalStats = []
for tag in tags:
    totalStats.append(trackTotals(tag))
for file in os.listdir(directory + "/seminar_testdata/test_tagged"):
    evalDoc = evalDoc + file + "\n"
    #file = "302.txt"            #For selecting specific files
    #Load the testing email and the generated one
    data = open(directory + "/seminar_testdata/test_tagged/" + file, "r")
    test = data.read()
    data.close()
    data = open(directory + "/seminar_testdata/test_untagged_output/" + insertString(file,3,"out"),"r")
    email = data.read()
    data.close()
    stats = []
    for tag in tags:
        for tracker in totalStats:
            if tag == tracker.tag:
                trackClass = tracker
        missing = False
        testHits = re.findall("<"+tag+">.*?</"+tag+">",test,re.DOTALL)
        emailHits = re.findall("<"+tag+">.*?</"+tag+">",email,re.DOTALL)
        if testHits == emailHits:
            correct = True
            target = None
            actual = None
            trackClass.incTP()
        else:
            if emailHits == []:
                missing = True
                trackClass.incFN()
            correct = False
            target = testHits
            actual = emailHits
            trackClass.incFP()
        tagStat = tagStats(tag,correct,missing,target,actual)
        stats.append(tagStat)
    evalDoc = evalDoc + present(stats) + "-------------------------------------\n"
    #break       #For selecting one file at a time

for tracker in totalStats:
    evalDoc = evalDoc + tracker.presentStats()

output = open(directory + "/evalOutput.txt","w")
output.write(evalDoc)
output.close()

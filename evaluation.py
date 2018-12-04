import os
import re
from os import listdir

def insertString(string,index,insert):
    return string[:index]+insert+string[index:]

directory = os.getcwd()
evalDoc = ""    #The final document evaluation
tags = ["speaker","stime","location","paragraph","sentence"]
for file in os.listdir(directory + "/seminar_testdata/test_tagged"):
    file = "301.txt"            #For selecting specific files
    #Load the testing email and the generated one
    data = open(directory + "/seminar_testdata/test_tagged/" + file, "r")
    test = data.read()
    data.close()
    data = open(directory + "/seminar_testdata/test_untagged_output/" + insertString(file,3,"out"),"r")
    email = data.read()
    data.close()
#<tag>(\S* *)</tag>

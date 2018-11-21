import nltk
import pickle
from os import listdir
from os.path import isfile, join
from nltk.tag import UnigramTagger
from nltk import word_tokenize

corpusRoot = 'nltk_data/corpora/brown/'
onlyfiles = [f for f in listdir(corpusRoot) if isfile(join(corpusRoot, f))]
corpus = nltk.corpus.reader.tagged.TaggedCorpusReader(corpusRoot, onlyfiles)

trainSents = corpus.tagged_sents()[:3000]
testSents = corpus.tagged_sents()[3000:]
unigramTagger = UnigramTagger(trainSents)
print("Test accuracy = "+str(unigramTagger.evaluate(testSents)))
fileName = 'tagfile'
fileObj = open(fileName,'wb')
pickle.dump(unigramTagger,fileObj)
fileObj.close()

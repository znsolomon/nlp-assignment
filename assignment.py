import nltk
from os import listdir
from os.path import isfile, join
from nltk.tag import UnigramTagger
corpusRoot = 'nltk_data/corpora/brown/'
onlyfiles = [f for f in listdir(corpusRoot) if isfile(join(corpusRoot, f))]
corpus = nltk.corpus.reader.plaintext.PlaintextCorpusReader(corpusRoot, onlyfiles)

trainSents = corpus.sents()[:3000]
testSents = corpus.sents()[3000:]
unigramTagger = UnigramTagger(trainSents)
unigramTagger.evaluate(testSents)

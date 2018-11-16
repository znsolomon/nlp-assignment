import nltk
from nltk.tokenize.punkt import PunktLanguageVars
text = word_tokenize("And now for something completely different")
print(text)
print(nltk.pos_tag(text))

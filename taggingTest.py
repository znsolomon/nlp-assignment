import nltk
from nltk import word_tokenize
text = word_tokenize("And now for something completely different")
print(text)
print(nltk.pos_tag(text))

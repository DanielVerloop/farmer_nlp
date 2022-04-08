import nltk
from nltk.stem import PorterStemmer

ps = PorterStemmer()

sentence = "The product leaves the machine and the stock reduce in 1 unit"
tokens = nltk.word_tokenize(sentence)
print(f"tokens: {tokens}")

tagged = nltk.pos_tag(tokens)
print(f"tag without stemming:{tagged}")

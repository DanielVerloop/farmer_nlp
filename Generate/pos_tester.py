import nltk
import stanfordnlp
from nltk import PorterStemmer
nlp = stanfordnlp.Pipeline(lang='en')
ps = PorterStemmer()
sentence = "then the vending machine asks for missing dollars"
print(sentence)
tokens = nltk.word_tokenize(sentence)
print(f"tokens: {tokens}")

tagged = nltk.pos_tag(tokens)
print(f"nltk tags: {tagged}")


def extract_verbs(pos_tags):
    verbs = []
    for word in range(0, len(pos_tags)):
        if pos_tags[word][1].startswith('VB'):
            verbs += [pos_tags[word][0]]
            print(ps.stem(pos_tags[word][0]))

    return verbs

def get_stanford_tags(sentence):
    nlp = stanfordnlp.Pipeline(lang='en', processors='tokenize,pos')
    tagger = nlp(sentence)
    result = [(word.text, word.pos) for word in tagger.sentences[0].words]
    return result

print(get_stanford_tags(sentence))

extract_verbs(get_stanford_tags(sentence))
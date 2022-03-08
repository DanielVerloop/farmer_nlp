import inspect
import sys
from gensim import corpora, models, similarities
from collections import defaultdict
from Generate.Banking.src.bank import BankAccount
from Generate.Banking.features.steps import steps

# paths for inspect to be able to access all modules
sys.path.append('../Generate/Banking/src')
# sys.path.append('Projects/bdd_behave/src')
# sys.path.append('Projects/Behave-Tutorial/src')
# sys.path.append('Projects/cis-troll-match/')
# sys.path.append('Projects/python_bdd/src/app/')
# sys.path.append('Projects/python-data-io-performance-tests/')
# sys.path.append('Projects/Banking/features/steps')
# sys.path.append('Projects/bdd_behave/src/features/steps')
# sys.path.append('Projects/cis-troll-match/features/steps')
# sys.path.append('Projects/python_bdd/src/app/features/steps')
# sys.path.append('Projects/python-data-io-performance-tests/features/steps')
# sys.path.append('Projects/Behave-Tutorial/src/steps')
#
# import steps
# import steps1
# #import steps2
# import steps3
# import steps4
# import steps5
#
# modules = [steps, steps1, steps3, steps4,steps5]
modules = [steps]


def get_paragraph(paragraph):
    paragraph_sentences = {}
    paragraph_tokens = {}

    sentences = paragraph.split("\n")

    scenario = sentences[0].strip()
    steps = []

    for i in range(1, len(sentences)):
        steps += [sentences[i].strip()]

    paragraph_sentences[scenario] = steps

    return paragraph_sentences

# paths = ["Projects/Banking/features/transactions.feature","Projects/bdd_behave/src/features/tutorial.feature","/home/ruxi/PycharmProjects/Match/Projects/Behave-Tutorial/src/.feature"
#          ,"Projects/python-data-io-performance-tests/features/csv-performance.feature","Projects/python_bdd/src/app/features/message_parsing.feature",
#          "/home/ruxi/PycharmProjects/Match/Projects/python_bdd/src/app/features/message_validity.feature"]

paths = ["../Generate/Banking/features/transactions.feature"]

# Processes a feature file
# separates all steps into singular lines(When, Given, Then)
# returns array of all steps
def process_file(path):
    feature_file = open(path)

    data = feature_file.read()

    all_paragraphs = data.split("\n\n")
    #print paragraphs

    paragraphs = []
    for paragraph in all_paragraphs:
        tempo = paragraph
        first_word = tempo.split(":")
        if first_word[0].strip() == "Scenario":
            paragraphs += [paragraph]

    documents = []

    for paragraph in paragraphs:
        final_paragraphs= get_paragraph(paragraph)
        scenarios = final_paragraphs.keys()
        for scenario in scenarios:
            steps = final_paragraphs[scenario]
            for step in steps:
                documents += [step.strip()]

    return documents
documents = []

for path in paths:
    documents += process_file(path)

for document in documents:
    if document is None:
        del document
print(f"documents: {documents}")


def get_similarities(documents, doc):
    # remove common words and tokenize
    stoplist = set('for a of the and to in'.split())
    texts = [[word for word in document.lower().split() if word not in stoplist] for document in documents]

    frequency = defaultdict(int)

    for text in texts:
        for token in text:
            frequency[token] += 1

    texts = [[token for token in text if frequency[token] > 1] for text in texts]

    dictionary = corpora.Dictionary(texts)
    #print dictionary
    corpus = [dictionary.doc2bow(text) for text in texts]

    #print corpus
    # serialize is used to process corpus that is larger than RAM
    # corpora.MmCorpus.serialize('/tmp/steps.mm',corpus)
    #
    # corpus = corpora.MmCorpus('/tmp/steps.mm')

    lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=2)

    vec_bow = dictionary.doc2bow(doc.lower().split())
    vec_lsi = lsi[vec_bow] # convert the query to LSI space
    #print (vec_lsi)

    index = similarities.MatrixSimilarity(lsi[corpus])

    sims = index[vec_lsi]

    sims = sorted(enumerate(sims), key=lambda item: -item[1])
    return (sims)

# Separate the @keyword + () from the step
def get_annotations(module, step):
    lines = inspect.getsourcelines(getattr(module, step))

    annotation = lines[0][0].replace("u'", "'").replace("')", "")
    annotation.replace("\\", "")
    annotation = annotation.split("('")[1]
    print(annotation)
    return annotation


for module in modules:
    for name,data in inspect.getmembers(module, inspect.isfunction):
        if name == '__builtins__':
            continue
        lines = inspect.getsourcelines(getattr(module, name))
        if (lines[0][0][:1] == '@'):
            annotation = get_annotations(module,name)
            print("Similarities for step: " + name)
            print(get_similarities(documents,annotation))



import inspect
import sys
import random
import nltk

import spacy
nlp = spacy.load('en_core_web_md')

# paths for inspect to be able to access all modules
sys.path.append('Projects/Banking/')
sys.path.append('Projects/bdd_behave/src')
sys.path.append('Projects/Behave-Tutorial/src')
sys.path.append('Projects/cis-troll-match/')
sys.path.append('Projects/python_bdd/src/app/')
sys.path.append('Projects/python-data-io-performance-tests/')
sys.path.append('Projects/Banking/features/steps')
sys.path.append('Projects/bdd_behave/src/features/steps')
sys.path.append('Projects/cis-troll-match/features/steps')
sys.path.append('Projects/python_bdd/src/app/features/steps')
sys.path.append('Projects/python-data-io-performance-tests/features/steps')
sys.path.append('Projects/Behave-Tutorial/src/steps')

import steps
import steps1
#import steps2
import steps3
import steps4
import steps5

modules = [steps, steps1, steps3, steps4,steps5]

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

paths = ["Projects/Banking/features/transactions.feature","Projects/bdd_behave/src/features/tutorial.feature","/home/ruxi/PycharmProjects/Match/Projects/Behave-Tutorial/src/.feature"
         ,"Projects/python-data-io-performance-tests/features/csv-performance.feature","Projects/python_bdd/src/app/features/message_parsing.feature",
         "/home/ruxi/PycharmProjects/Match/Projects/python_bdd/src/app/features/message_validity.feature"]
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
print (documents)


def get_similarities(documents, doc):
    similarities = {}
    main_doc = nlp(doc)
    main_doc_no_stop_words = nlp(' '.join([str(t) for t in main_doc if not t.is_stop]))
    for dc in documents:
        search_doc = nlp(dc)
        search_doc_no_stop_words = nlp(' '.join([str(t) for t in search_doc if not t.is_stop]))
        similarities[dc] = main_doc.similarity(search_doc)

    max_similarity = max(list(similarities.values()))

    for d in similarities:
        if similarities[d] == max_similarity:
            return d

def get_annotations(module, step):
    lines = inspect.getsourcelines(getattr(module, step))

    annotation = lines[0][0].replace("u'", "'").replace("')", "")
    annotation.replace("\\", "")
    print (annotation)
    return annotation.split("('")[1]


for module in modules:
    for name,data in inspect.getmembers(module, inspect.isfunction):
        if name == '__builtins__':
            continue
        lines = inspect.getsourcelines(getattr(module, name))
        if (lines[0][0][:1] == '@'):
            annotation = get_annotations(module,name)
            print ("Similarities for step: " + name)
            print (get_similarities(documents,annotation))




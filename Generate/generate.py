import os
import nltk
from nltk import PorterStemmer
import re
import json
from projects import paths
from parse import process_file
from allennlp_models import pretrained
import stanfordnlp

# download the nltk pos-tagger
nltk.download('averaged_perceptron_tagger')
ps = PorterStemmer()
# backup standford pos-tagger
nlp = stanfordnlp.Pipeline(lang='en', processors='tokenize,pos')

# import allennlp srl model
predictor = pretrained.load_predictor("structured-prediction-srl-bert")

# extract list of quoted values from a string
def get_quoted(sentence):
    quoted = []

    quoted_re = re.compile('"[^"]*"')
    for value in quoted_re.findall(sentence):
        quoted += [value.replace('"', '').strip()]
    return quoted


# check that something does not contain numbers
def check_not_number(numbers, value):
    not_number = True
    for number in numbers:
        if str(number) in value:
            not_number = False
    return not_number


# return the first noun from a sequence
def check_noun(sequence):
    text = nltk.word_tokenize(sequence)
    result = nltk.pos_tag(text)

    for word in result:
        if word[1].startswith("NN"):
            return word[0]


# get sentence words with their part of speach tags
def get_pos(sentence):
    text = nltk.word_tokenize(sentence)
    result = nltk.pos_tag(text)

    return result

def get_stanford_pos(sentence):
    tagger = nlp(sentence)
    result = [(word.text, word.pos) for word in tagger.sentences[0].words]
    return result

def extract_nouns_and_values(pos_tags):
    nouns = []
    values = []
    for word in range(0, len(pos_tags)):
        if pos_tags[word][1].startswith("NN"):
            if word + 1 < len(pos_tags):  # out-of-bound protection
                if pos_tags[word + 1][1].startswith("NN"):
                    nouns += [pos_tags[word][0] + " " + pos_tags[word + 1][0]]
                    word += 1
                else:
                    nouns += [pos_tags[word][0]]
            else:
                nouns += [pos_tags[word][0]]
        if pos_tags[word][1] == "CD":
            values += [pos_tags[word][0]]
    if (pos_tags[len(pos_tags) - 1][1] == "NN") and pos_tags[len(pos_tags) - 1][0] not in nouns:
        nouns += [pos_tags[len(pos_tags) - 1][0]]

    return nouns #, values


def extract_verbs(pos_tags):
    verbs = []
    stemmed = []
    for word in range(0, len(pos_tags)):
        if pos_tags[word][1].startswith('VB'):
            verbs += [pos_tags[word][0]]
            stemmed += [ps.stem(pos_tags[word][0])]

    return verbs, stemmed


# generate test cases and append them to the file
def extract_params(printable_sentence):
    params = []
    # no datatables are present
    if "<" and ">" not in printable_sentence:
        return None, printable_sentence

    words = printable_sentence.strip().split(' ')
    for i in range(0, len(words)):
        if words[i].startswith('<') and words[i].endswith('>'):
            words[i] = words[i].replace('>', '').replace('<', '')
            params.append(words[i])
    sentence = ' '.join(words)

    return params, sentence


def clean_verbs(verbs, stemmed, parameters):
    for i in range(0, len(verbs)):
        if verbs[i] in parameters:
            del verbs[i]
            del stemmed[i]

    return verbs, stemmed


def generate(sentence, json_object):
    #JSON data structures
    givenJSON = {} if json_object['given'] == {} else json_object['given']
    whenJSON = {} if json_object['when'] == {} else json_object['when']
    thenJSON = {} if json_object['then'] == {} else json_object['then']
    # And steps
    gAndJSON = [] if json_object['gAnd'] == [] else json_object['gAnd']
    wAndJSON = [] if json_object['wAnd'] == [] else json_object['wAnd']
    tAndJSON = [] if json_object['tAnd'] == [] else json_object['tAnd']

    # extract table values first (between < & >) and clean the sentence
    # then use the pos-tagger
    parameters, cleaned_sentence = extract_params(sentence)
    if parameters is None:
        parameters = []
    pos_tags = get_pos(cleaned_sentence)

    verbs, stemmed_verbs = extract_verbs(pos_tags)
    if verbs == []:
        verbs, stemmed_verbs = extract_verbs(get_stanford_pos(sentence))

    cleaned_verbs, stemmed_verbs = clean_verbs(verbs, stemmed_verbs, parameters)

    # extract nouns and cardinals
    nouns = extract_nouns_and_values(pos_tags)

    # Given step
    if "Given" in sentence:
        quoted_values = []
        quotes = get_quoted(sentence)
        # TODO:handle quoted values: "<number>" will become number
        for quote in quotes:
            if '>' in quote:
                quote = quote.replace('>', '').replace('<', '')
            elif len(quote) > 1 and quote.isdigit() is not True:
                quote = '"' + quote + '"'
            quoted_values += [quote]

        # extract numbers
        number = [int(s) for s in sentence.split() if s.isdigit()]

        # put analysis into json object
        info = {'nouns': nouns, 'numbers': number, 'parameters': parameters}
        givenJSON = {"description": cleaned_sentence, "analysis": [info]}

    # When step
    if "When" in sentence:
        # extract numbers
        number_values = [int(s) for s in sentence.split() if s.isdigit()]

        # TODO: use values and parameters to make possible param list
        quoted_values = []
        quotes = get_quoted(sentence)
        for quote in quotes:
            if '>' in quote:
                quote = quote.replace('>', '').replace('<', '')
            elif len(quote) > 1 and quote.isdigit() is not True:
                quote = '"' + quote + '"'
            quoted_values += [quote]

        # create semantic role labeling format
        srl_sentence = predictor.predict(
            sentence=sentence
        )

        srl_analysis = get_srl(srl_sentence, stemmed_verbs, cleaned_verbs)
        info = {'nouns': nouns, 'numbers': number_values, 'parameters': parameters}

        whenJSON = {"description": cleaned_sentence, "analysis": [info, srl_analysis]}

    # Then steps
    if "Then" in sentence:

        # extract numbers
        number_values = [int(s) for s in sentence.split() if s.isdigit()]

        quoted_values = []

        info = {'nouns': nouns, 'numbers': number_values, 'parameters': parameters}

        # handle quoted values
        quotes = get_quoted(sentence)

        srl_sentence = predictor.predict(
            sentence=sentence
        )
        # TODO:add quotes to json
        for quote in quotes:
            if '>' in quote:
                quote = quote.replace('>', '').replace('<', '')
            elif len(quote) > 1 and quote.isdigit() is not True:
                quote = '"' + quote + '"'
            quoted_values += [quote]

        srl_analysis = get_srl(srl_sentence, stemmed_verbs, cleaned_verbs)

        thenJSON = {"description": cleaned_sentence, "analysis": [info, srl_analysis]}

    # And steps
    if "And" in sentence:
        # extract numbers
        number_values = [int(s) for s in sentence.split() if s.isdigit()]

        info = {'nouns': nouns, 'numbers': number_values, 'parameters': parameters}


        # handle quoted values
        quotes = get_quoted(sentence)

        srl_sentence = predictor.predict(
            sentence=sentence
        )
        # TODO:add quotes to json
        for quote in quotes:
            if '>' in quote:
                quote = quote.replace('>', '').replace('<', '')
            elif len(quote) > 1 and quote.isdigit() is not True:
                quote = '"' + quote + '"'
            quoted_values += [quote]

        srl_analysis = get_srl(srl_sentence,stemmed_verbs, cleaned_verbs)

        # add the result to the correct type
        if givenJSON != {} and (whenJSON == {} and thenJSON == {}):
            json_object["gAnd"].append({"description": cleaned_sentence, "analysis": [info, srl_analysis]})
        if whenJSON != {} and thenJSON == {}:
            json_object["wAnd"].append({"description": cleaned_sentence, "analysis": [info, srl_analysis]})
        if thenJSON != {}:
            json_object["tAnd"].append({"description": cleaned_sentence, "analysis": [info, srl_analysis]})

    json_object["given"] = givenJSON
    json_object["when"] = whenJSON
    json_object["then"] = thenJSON
    return json_object


def get_srl(srl_sentence, stemmed,  verbs):
    srl_analysis = []
    if len(verbs) > 0:
        arguments = []

        for i in range(0, len(verbs)):
            description = ""

            # Get the label description
            for srl in srl_sentence['verbs']:
                if srl['verb'] == verbs[i]:
                    description = srl['description']

            # replace useless characters
            description = description.replace('[', '').replace('<', '').replace('>', '').split(']')
            description = [pair.strip() for pair in description]
            if '' in description:  # remove empty strings
                description.remove('')

            srl_analysis.append([stemmed[i], description])
    return srl_analysis


# generate tests for project
# path = path to gherkin file
# TODO: add support for multiple files to be processed at once
def generate_for_project(paths):
    completeNLP2JSON = {  # Dictionary to hold JSON data for output of NLP processing of all feature files
        "files": []
    }
    files = []
    for path in paths:
        print(os.path.basename(path))

        file2JSON = {  # Dictionary to hold NLP processing results of 1 file
            "name": os.path.basename(path),
            "scenarios": []
        }

        # parse Gherkin scenarios

        documents = process_file(path)
        grouped_docs = []
        scenario = []
        for doc in documents:
            if (not scenario == []) and doc.startswith("Given"):
                grouped_docs.append(scenario)
                scenario = []
            scenario.append(doc)
        grouped_docs.append(scenario)  # add last scenario to grouped

        # process scenarios
        for group in grouped_docs:
            # for reference
            scenario2JSON = {
                "given": {},
                "gAnd": [],
                "when": {},
                "wAnd": [],
                "then": {},
                "tAnd": [],
            }
            result = [] if file2JSON['scenarios'] == [] else file2JSON['scenarios']
            for step in group:
                scenario2JSON = generate(step, scenario2JSON)
            result.append(scenario2JSON)
            file2JSON["scenarios"] = result

        # add a processed file to list
        files.append(file2JSON)

    # complete the json object
    completeNLP2JSON["files"] = files

    # dump result to json file
    with open("nlp_results.json", "w") as write_file:
        json.dump(completeNLP2JSON, write_file, indent=2)


generate_for_project(paths)
# # print(process_file(paths[1]))

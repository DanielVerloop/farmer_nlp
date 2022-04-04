import os
import nltk
import re
import json
from projects import paths
from parse import process_file
from allennlp_models import pretrained

# download the nltk pos-tagger
nltk.download('averaged_perceptron_tagger')

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


def extract_nouns_and_values(pos_tags):
    nouns = []
    values = []
    for word in range(0, len(pos_tags)):
        if pos_tags[word][1] == "NN":
            if word + 1 < len(pos_tags):  # out-of-bound protection
                if pos_tags[word + 1][1] == "NN":
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

    return nouns, values


def extract_verbs(pos_tags):
    verbs = []
    for word in range(0, len(pos_tags)):
        if pos_tags[word][1].startswith('VB'):
            verbs += [pos_tags[word][0]]
    return verbs


# global variables for object, class and attribute names

class_name = ""
attribute_version = ""
class_version = ""


# generate test cases and append them to the file
def generate(sentence, json_object):
    global f
    pos_tags = get_pos(sentence)

    printable_sentence = sentence

    givenJSON = {} if json_object['given'] == {} else json_object['given']
    whenJSON = {} if json_object['when'] == {} else json_object['when']
    thenJSON = {} if json_object['then'] == {} else json_object['then']
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

        # extract nouns and cardinals
        nouns, values = extract_nouns_and_values(pos_tags)

        # extract numbers
        number = [int(s) for s in sentence.split() if s.isdigit()]

        # put analysis into json object
        info = {'nouns': nouns, 'numbers': number, 'parameters': values}
        givenJSON = {"description": printable_sentence, "analysis": [info]}

    # When step
    if "When" in sentence:

        # extract numbers
        number_values = [int(s) for s in sentence.split() if s.isdigit()]
        nouns, values = extract_nouns_and_values(pos_tags)

        # TODO: extract and handle quoted values
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

        verbs = extract_verbs(pos_tags)
        srl_analysis = []
        info = {'nouns': nouns, 'numbers': number_values}
        if len(verbs) > 0:
            arguments = []

            for verb in verbs:
                description = ""

                # Get the label description
                for srl in srl_sentence['verbs']:
                    if srl['verb'] == verb:
                        description = srl['description']

                # replace useless characters
                description = description.replace('[', '').replace('<', '').replace('>', '').split(']')
                description = [pair.strip() for pair in description]
                if '' in description:  # remove empty strings
                    description.remove('')
                # go through list of arguments and extract values, nouns, compounds
                # basically useful info from arguments
                # for arg in description:
                #     value = arg.split(':')
                #     role = ""
                #     if len(value) > 1:
                #         role = value[0].strip()
                #         value = value[1]
                #     else:
                #         val = value[0]
                #         value = val
                #     if "and" in value:
                #         multiple_values = value.split("and")
                #         for val in multiple_values:
                #             arguments += [val.strip()]
                #
                #     # ignore arguments we don't need
                #     elif len(number_values) > 0:
                #         if value.strip() not in ["I", "We", "i",
                #                                  "we"] and role != "ARGM-TMP" and role != "V" and role != "ARG2":
                #             if len(value.strip().split(" ")) > 1:
                #                 if check_noun(value) is not None:
                #                     arguments += [check_noun(value)]
                #             else:
                #                 arguments += [value.strip()]
                #     else:
                #         if value.strip() not in ["I", "We", "i",
                #                                  "we"] and role != "ARGM-TMP" and role != "V" and value != "":
                #             if len(value.strip().split(" ")) > 1:
                #                 if check_noun(value) is not None:
                #                     arguments += [check_noun(value)]
                #             else:
                #                 arguments += [value.strip()]
                #
                # # # create list of function arguments, including information from srl arguments and quoted values
                # function_arguments = ""
                #
                # for val in arguments:
                #     if len(number_values) > 1:
                #         if str(number_values[0]) not in val and str(number_values[1]) not in val:
                #             function_arguments += val.strip() + ", "
                #     elif len(number_values) > 0:
                #         if str(number_values[0]) not in val:
                #             function_arguments += val.strip() + ", "
                #     else:
                #         if val.strip().isdigit() is not True and '"' not in val and val != "":
                #             if len(val.split(" ")) > 1:
                #                 if check_noun(val) is not None:
                #                     function_arguments += check_noun(val.strip()) + ", "
                #             else:
                #                 function_arguments += val.strip() + ", "
                #
                # for quote in quoted_values:
                #     if '"' not in quote and quote not in function_arguments:
                #         function_arguments += quote + ", "

                srl_analysis.append([verb, description])

        whenJSON = {"description": printable_sentence, "analysis": [info, srl_analysis]}

    # Then steps
    if "Then" in sentence:

        # extract numbers
        number_values = [int(s) for s in sentence.split() if s.isdigit()]
        nouns, values = extract_nouns_and_values(pos_tags)
        info = {'nouns': nouns, 'numbers': number_values}
        verbs = extract_verbs(pos_tags)
        quoted_values = []

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

        srl_analysis = []
        info = {'nouns': nouns, 'numbers': number_values}
        if len(verbs) > 0:
            arguments = []

            for verb in verbs:
                description = ""

                # Get the label description
                for srl in srl_sentence['verbs']:
                    if srl['verb'] == verb:
                        description = srl['description']

                # replace useless characters
                description = description.replace('[', '').replace('<', '').replace('>', '').split(']')
                description = [pair.strip() for pair in description]
                if '' in description:  # remove empty strings
                    description.remove('')

                srl_analysis.append([verb, description])

        thenJSON = {"description": printable_sentence, "analysis": [info, srl_analysis]}

    json_object["given"] = givenJSON
    json_object["when"] = whenJSON
    json_object["then"] = thenJSON
    return json_object


# generate tests for project
# path = path to gherkin file
# TODO: add support for multiple files to be processed at once
def generate_for_project(path):
    print(os.path.basename(path))
    completeNLP2JSON = {  # Dictionary to hold JSON data for output of NLP processing of all feature files
        "files": []
    }
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
    grouped_docs.append(scenario) #add last scenario to grouped

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

    completeNLP2JSON["files"].append(file2JSON)
    # dump result to json file
    with open("nlp_results.json", "w") as write_file:
        json.dump(completeNLP2JSON, write_file, indent=2)


for i in range(0, len(paths)):
    generate_for_project(paths[i])


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

    givenJSON = [] if json_object['scenarios']['given'] == {} else json_object['scenarios']['given']
    whenJSON = [] if json_object['scenarios']['when'] == {} else json_object['scenarios']['when']
    thenJSON = [] if json_object['scenarios']['then'] == {} else json_object['scenarios']['then']
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
        givenJSON.append({"description": printable_sentence, "analysis": [info]})

        # extract object, class and attribute names - global to be able to access for next steps as well
        # output to file
        # f.write("    context." + attribute_version + " = " + class_version + "(")
        # add numerical values
        #
        # if len(number) == 1:
        #     f.write(str(number[0]) + ")\n")
        # elif len(number) > 1:
        #     for word in range(0, len(number) - 1):
        #         f.write(str(number[word]) + ",")
        #     f.write(str(number[len(number) - 1]))
        #     f.write(")\n")
        #
        # # add quoted values
        #
        # elif len(quoted_values) == 1:
        #     f.write(quoted_values[0] + ")\n")
        # elif len(quoted_values) > 1:
        #     for word in range(0, len(quoted_values) - 1):
        #         f.write(quoted_values[word] + ",")
        #     f.write(quoted_values[len(quoted_values) - 1])
        #     f.write(")\n")
        #
        # # add any other values
        #
        # else:
        #     if len(values) > 1:
        #         for word in range(0, len(values) - 1):
        #             f.write(values[word] + ",")
        #         f.write(values[len(values) - 1])
        #         f.write(")\n")
        #     else:
        #         f.write(")\n")
        # f.write("\n")

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
            whenJSON.append({"description": printable_sentence, "analysis": [info, srl_analysis]})

        # if len(srl_sentence['verbs']) > 0:
        #
        #     # extract verb and description
        #     verb = srl_sentence['verbs'][0]['verb']
        #     description = srl_sentence['verbs'][0]['description']
        #
        #     # replace useless characters
        #     description = description.replace('[', '').replace('<', '').replace('>', '').split(']')
        #
        #     # go through list of arguments and extract values, nouns, compounds - basically useful info from arguments
        #     for arg in description:
        #         value = arg.split(':')
        #         role = ""
        #         if len(value) > 1:
        #             role = value[0].strip()
        #             value = value[1]
        #         else:
        #             val = value[0]
        #             value = val
        #         if "and" in value:
        #             multiple_values = value.split("and")
        #             for val in multiple_values:
        #                 arguments += [val.strip()]
        #
        #         # ignore arguments we don't need
        #         elif len(number_values) > 0:
        #             if value.strip() not in ["I", "We", "i",
        #                                      "we"] and role != "ARGM-TMP" and role != "V" and role != "ARG2":
        #                 if len(value.strip().split(" ")) > 1:
        #                     if check_noun(value) is not None:
        #                         arguments += [check_noun(value)]
        #                 else:
        #                     arguments += [value.strip()]
        #         else:
        #             if value.strip() not in ["I", "We", "i",
        #                                      "we"] and role != "ARGM-TMP" and role != "V" and value != "":
        #                 if len(value.strip().split(" ")) > 1:
        #                     if check_noun(value) is not None:
        #                         arguments += [check_noun(value)]
        #                 else:
        #                     arguments += [value.strip()]
        #
        #     # # create list of function arguments, including information from srl arguments and quoted values
        #     function_arguments = ""
        #
        #     for val in arguments:
        #         if len(number_values) > 1:
        #             if str(number_values[0]) not in val and str(number_values[1]) not in val:
        #                 function_arguments += val.strip() + ", "
        #         elif len(number_values) > 0:
        #             if str(number_values[0]) not in val:
        #                 function_arguments += val.strip() + ", "
        #         else:
        #             if val.strip().isdigit() is not True and '"' not in val and val != "":
        #                 if len(val.split(" ")) > 1:
        #                     if check_noun(val) is not None:
        #                         function_arguments += check_noun(val.strip()) + ", "
        #                 else:
        #                     function_arguments += val.strip() + ", "
        #
        #     for quote in quoted_values:
        #         if '"' not in quote and quote not in function_arguments:
        #             function_arguments += quote + ", "
        #
        #     print(f"args:{function_arguments}")
        #     # create output

        #     f.write("@when('" + printable_sentence + "') \n")
        #     if len(function_arguments) > 2:
        #         f.write("def step_impl(context, " + function_arguments[:-2] + "): \n")
        #     else:
        #         f.write("def step_impl(context): \n")
        #     f.write("    context." + attribute_version + "." + verb + "(")
        #
        #     if len(number_values) == 1:
        #         f.write(str(number_values[0]) + ")\n")
        #     elif len(number_values) > 1:
        #         for word in range(0, len(number_values) - 1):
        #             f.write(str(number_values[word]) + ",")
        #         f.write(str(number_values[len(number_values) - 1]))
        #         f.write(")\n")
        #     elif len(quoted_values) == 1:
        #         f.write(quoted_values[0] + ")\n")
        #     elif len(quoted_values) > 1:
        #         for word in range(0, len(quoted_values) - 1):
        #             f.write(quoted_values[word] + ",")
        #         f.write(quoted_values[len(quoted_values) - 1])
        #         f.write(")\n")
        #     else:
        #         if len(arguments) > 0:
        #             for word in range(0, len(arguments) - 1):
        #                 f.write(arguments[word] + ",")
        #             f.write(arguments[len(arguments) - 1])
        #             f.write(")\n")
        #         else:
        #             f.write(")\n")
        #     f.write("\n")
        # else:
        #     f.write("@when('" + printable_sentence + "') \n")
        #     f.write("def step_impl(context): \n")
        #     f.write("    pass \n")
        #     f.write("\n")

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

        # if there are no numbers in the sentence
        if len(number_values) == 0:

            # create semantic role labeling format

            if len(srl_sentence['verbs']) > 0:

                # extract description and replace useless characters
                description = srl_sentence['verbs'][0]['description']
                description = description.replace('[', '').replace('<', '').replace('>', '').split(']')

                arguments = []

                # extract useful info from arguments - nouns, compounds, etc.
                for arg in description:
                    value = arg.split(':')
                    if len(value) > 1:
                        role = value[0].strip()
                        value = value[1]
                        if "and" in value:
                            multiple_values = value.split("and")
                            for val in multiple_values:
                                arguments += [val.strip()]
                        # ignore useless arguments or sequences
                        elif value.strip() not in ["I", "We", "i", "we"] and role != "ARGM-TMP" and role != "V":
                            arguments += [
                                value.replace("the", '').replace("a ", '').replace("should ", '').replace(" be ",
                                                                                                          '').replace(
                                    "is ", '')]

                arguments += [
                    description[len(description) - 1].strip().replace('"', "").replace("the", '').replace("a ",
                                                                                                          '').replace(
                        "should ", '').replace(" be ", '').replace("is ", '').replace("equal to", "")]

                f.write("@then('" + printable_sentence + "') \n")

                # Add analysis to json
                thenJSON.append({"description": printable_sentence, "analysis": [pos_tags, srl_sentence]})

                # create list of function arguments, including information from srl arguments and quoted values
                function_arguments = ""
                for val in arguments:
                    if val.strip() != attribute_version and '"' not in val and val.strip().isdigit() is not True:
                        if check_noun(val) is not None:
                            function_arguments += check_noun(val.strip()) + ", "
                for quote in quoted_values:
                    if '"' not in quote and quote not in function_arguments:
                        function_arguments += quote + ", "
                if function_arguments != "":
                    f.write("def step_impl(context, " + function_arguments[:-2] + "): \n")
                else:
                    f.write("def step_impl(context): \n")

                # identify comparison value for assert statement

                if len(quoted_values) > 0:
                    comparison_value = quoted_values[0]
                else:
                    comparison_value = arguments[len(arguments) - 1].strip()
                    if check_noun(comparison_value) is not None:
                        comparison_value = check_noun(comparison_value)
                comparison_attribute = "insert_attribute_to_compare"

                for arg in arguments:
                    if attribute_version not in arg.strip() and arg.strip() != comparison_value:
                        comparison_attribute = arg.strip()
                        if check_noun(comparison_attribute) is not None:
                            comparison_attribute = check_noun(comparison_attribute)
                        break

                # output to steps.py file
                # TODO: replace by own component
                f.write(
                    "    assert context." + attribute_version + "." + comparison_attribute + " == " + comparison_value + "\n")

                f.write("\n")
            else:
                f.write("@then('" + printable_sentence + "') \n")
                f.write("def step_impl(context): \n")
                f.write("    pass \n")
                f.write("\n")

        # if there are numbers in the sentence then focus on nouns and cardinals
        else:
            nouns = []

            # extract nouns

            for word in range(0, len(pos_tags)):
                if pos_tags[word][1] == "NN":
                    nouns += [pos_tags[word][0]]

            # identify comparison value for assert statement

            if len(number_values) > 0:
                comparison_value = str(number_values[0])
            elif len(quoted_values) > 0:
                comparison_value = quoted_values[0]
            else:
                comparison_value = nouns[len(nouns) - 1].replace("equal to", "").strip()

            comparison_attribute = "insert_attribute_to_compare"
            for noun in nouns:
                if noun != attribute_version and noun != comparison_value:
                    comparison_attribute = noun

            # Add analysis to json
            thenJSON.append({"description": printable_sentence, "analysis": [pos_tags, srl_sentence["verbs"]]})
            # output to steps.py file
            # TODO: replace by own component
            f.write("@then('" + printable_sentence + "') \n")
            f.write("def step_impl(context): \n")
            f.write(
                "    assert context." + attribute_version + "." + comparison_attribute + " == " + comparison_value + "\n")

            f.write("\n")

    json_object["scenarios"]["given"] = givenJSON
    json_object["scenarios"]["when"] = whenJSON
    json_object["scenarios"]["then"] = thenJSON
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
        "scenarios": {
            "given": {},
            "when": {},
            "then": {}
        }
    }

    # parse Gherkin scenarios
    documents = process_file(path)

    for doc in documents:
        file2JSON = generate(doc, file2JSON)

    completeNLP2JSON["files"].append(file2JSON)
    # dump result to json file
    with open("nlp_results.json", "w") as write_file:
        json.dump(completeNLP2JSON, write_file, indent=2)


for i in range(0, len(paths)):
    f = open("generated_code/generated_steps_" + str(i) + ".py", "a+")
    f.write("from behave import * \n")
    f.write("\n")

    generate_for_project(paths[i])
# # generate tests for projects in the given paths - used for the experiments
# for i in range(0, len(paths)):
#
#     documents = process_file(paths[i])
#
#     class_name = "insert_class_name"
#     attribute_version = "insert_attribute_version"
#     class_version = "insert_class_version"
#
#     # create file
#     # if exists, appends existing file
#     # TODO: look for a way to add imports in a better manner
#     #  generally improve the code generation with its own component
#     f = open("generated_code/generated_steps_" + str(i) + ".py", "a+")
#
#     f.write("from behave import * \n")
#
#     f.write("\n")
#
#     for doc in documents:
#         generate(doc)

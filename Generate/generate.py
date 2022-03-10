import nltk
import re
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
        if word[1] == "NN":
            return word[0]


# get sentence words with their part of speach tags
def get_pos(sentence):
    text = nltk.word_tokenize(sentence)
    result = nltk.pos_tag(text)

    return result


# global variables for object, class and attribute names

class_name = ""
attribute_version = ""
class_version = ""

# create file
f = open("generated_steps.py", "a+")
f.write("from behave import * \n")
f.write("\n")


# generate test cases and append them to the file
def generate(sentence):
    global f
    pos_tags = get_pos(sentence)

    code = ""

    context = []

    printable_sentence = sentence

    # Given step

    if "Given" in sentence:

        nouns = []
        values = []

        quoted_values = []
        quotes = get_quoted(sentence)

        # handle quoted values: "<number>" will become number
        for quote in quotes:
            if '>' in quote:
                quote = quote.replace('>', '').replace('<', '')
            elif len(quote) > 1 and quote.isdigit() is not True:
                quote = '"' + quote + '"'
            quoted_values += [quote]

        # extract nouns and cardinals
        word: int
        for word in range(0, len(pos_tags) - 1):
            if pos_tags[word][1] == "NN":
                if pos_tags[word + 1][1] == "NN":
                    nouns += [pos_tags[word][0] + " " + pos_tags[word + 1][0]]
                    word += 1
                else:
                    nouns += [pos_tags[word][0]]
            if pos_tags[word][1] == "CD":
                values += [pos_tags[word][0]]
        if (pos_tags[len(pos_tags) - 1][1] == "NN") and pos_tags[len(pos_tags) - 1][0] not in nouns:
            nouns += [pos_tags[len(pos_tags) - 1][0]]

        # extract numbers
        number = [int(s) for s in sentence.split() if s.isdigit()]

        # start output
        f.write("@given('" + printable_sentence + "') \n")
        f.write("def step_impl(context): \n")

        # extract object, class and attribute names - global to be able to access for next steps as well
        global attribute_version, class_version, class_name
        print(f"attribute_version: {attribute_version}, class_v: {class_version}, class_name: {class_name}")

        if len(nouns) > 0:
            class_name = nouns[0]

        if " " in class_name:
            attribute_version = class_name.replace(" ", "_")
            split = class_name.split(" ")
            class_version = split[0].capitalize() + split[1].capitalize()
        else:
            attribute_version = class_name
            class_version = class_name.capitalize()

        print(f"attribute_version: {attribute_version}, class_v: {class_version}, class_name: {class_name}")
        # output to file
        f.write("    context." + attribute_version + " = " + class_version + "(")

        # add numerical values

        if len(number) == 1:
            f.write(str(number[0]) + ")\n")
        elif len(number) > 1:
            for word in range(0, len(number) - 1):
                f.write(str(number[word]) + ",")
            f.write(str(number[len(number) - 1]))
            f.write(")\n")

        # add quoted values

        elif len(quoted_values) == 1:
            f.write(quoted_values[0] + ")\n")
        elif len(quoted_values) > 1:
            for word in range(0, len(quoted_values) - 1):
                f.write(quoted_values[word] + ",")
            f.write(quoted_values[len(quoted_values) - 1])
            f.write(")\n")

        # add any other values

        else:
            if len(values) > 1:
                for word in range(0, len(values) - 1):
                    f.write(values[word] + ",")
                f.write(values[len(values) - 1])
                f.write(")\n")
            else:
                f.write(")\n")
        f.write("\n")

    # When step

    if "When" in sentence:

        # extract numbers

        number_values = [int(s) for s in sentence.split() if s.isdigit()]

        # extract and handle quoted values

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

        verb = ""
        description = ""

        if len(srl_sentence['verbs']) > 0:

            # extract verb and description
            verb = srl_sentence['verbs'][0]['verb']
            description = srl_sentence['verbs'][0]['description']

            arguments = []

            # replace useless characters
            description = description.replace('[', '').replace('<', '').replace('>', '').split(']')

            # go through list of arguments and extract values, nouns, compounds - basically useful info from arguments
            for arg in description:
                value = arg.split(':')
                print(value)
                role = ""
                if len(value) > 1:
                    role = value[0].strip()
                    value = value[1]
                else:
                    val = value[0]
                    value = val
                if "and" in value:
                    multiple_values = value.split("and")
                    for val in multiple_values:
                        arguments += [val.strip()]

                # ignore arguments we don't need
                elif len(number_values) > 0:
                    if value.strip() not in ["I", "We", "i",
                                             "we"] and role != "ARGM-TMP" and role != "V" and role != "ARG2":
                        if len(value.strip().split(" ")) > 1:
                            if check_noun(value) is not None:
                                arguments += [check_noun(value)]
                        else:
                            arguments += [value.strip()]
                else:
                    if value.strip() not in ["I", "We", "i",
                                             "we"] and role != "ARGM-TMP" and role != "V" and value != "":
                        if len(value.strip().split(" ")) > 1:
                            if check_noun(value) is not None:
                                arguments += [check_noun(value)]
                        else:
                            arguments += [value.strip()]

            # # create list of function arguments, including information from srl arguments and quoted values

            function_arguments = ""

            for val in arguments:
                if len(number_values) > 1:
                    if str(number_values[0]) not in val and str(number_values[1]) not in val:
                        function_arguments += val.strip() + ", "
                elif len(number_values) > 0:
                    if str(number_values[0]) not in val:
                        function_arguments += val.strip() + ", "
                else:
                    if val.strip().isdigit() is not True and '"' not in val and val != "":
                        if len(val.split(" ")) > 1:
                            if check_noun(val) is not None:
                                function_arguments += check_noun(val.strip()) + ", "
                        else:
                            function_arguments += val.strip() + ", "

            for quote in quoted_values:
                if '"' not in quote and quote not in function_arguments:
                    function_arguments += quote + ", "

            # create output
            # TODO: change this with own component
            f.write("@when('" + printable_sentence + "') \n")
            if len(function_arguments) > 2:
                f.write("def step_impl(context, " + function_arguments[:-2] + "): \n")
            else:
                f.write("def step_impl(context): \n")
            f.write("    context." + attribute_version + "." + verb + "(")

            if len(number_values) == 1:
                f.write(str(number_values[0]) + ")\n")
            elif len(number_values) > 1:
                for word in range(0, len(number_values) - 1):
                    f.write(str(number_values[word]) + ",")
                f.write(str(number_values[len(number_values) - 1]))
                f.write(")\n")
            elif len(quoted_values) == 1:
                f.write(quoted_values[0] + ")\n")
            elif len(quoted_values) > 1:
                for word in range(0, len(quoted_values) - 1):
                    f.write(quoted_values[word] + ",")
                f.write(quoted_values[len(quoted_values) - 1])
                f.write(")\n")
            else:
                if len(arguments) > 0:
                    for word in range(0, len(arguments) - 1):
                        f.write(arguments[word] + ",")
                    f.write(arguments[len(arguments) - 1])
                    f.write(")\n")
                else:
                    f.write(")\n")
            f.write("\n")
        else:
            f.write("@when('" + printable_sentence + "') \n")
            f.write("def step_impl(context): \n")
            f.write("    pass \n")
            f.write("\n")

    # Then steps

    if "Then" in sentence:

        # extract numbers
        number_values = [int(s) for s in sentence.split() if s.isdigit()]

        quoted_values = []

        # handle quoted values
        quotes = get_quoted(sentence)

        for quote in quotes:
            if '>' in quote:
                quote = quote.replace('>', '').replace('<', '')
            elif len(quote) > 1 and quote.isdigit() is not True:
                quote = '"' + quote + '"'
            quoted_values += [quote]

        # if there are no numbers in the sentence
        if len(number_values) == 0:

            # create semantic role labeling format
            srl_sentence = predictor.predict(
                sentence=sentence
            )

            if len(srl_sentence['verbs']) > 0:

                # extract description and replace useless characters
                description = srl_sentence['verbs'][0]['description']
                description = description.replace('[', '').replace('<', '').replace('>', '').split(']')

                arguments = []

                # extract useful info from arguments - nouns, compounds, etc.
                for arg in description:
                    value = arg.split(':')
                    print(value)
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

            # output to steps.py file

            f.write("@then('" + printable_sentence + "') \n")
            f.write("def step_impl(context): \n")
            f.write(
                "    assert context." + attribute_version + "." + comparison_attribute + " == " + comparison_value + "\n")

            f.write("\n")

    print("Done!")


# generate tests for project
# path = path to gherkin file 
def generate_for_project(path):
    documents = process_file(path)
    class_name = "insert_class_name"
    attribute_version = "insert_attribute_version"
    class_version = "insert_class_version"

    # create file
    f = open("features/steps/steps.py", "a+")

    f.write("from behave import * \n")

    f.write("\n")

    for doc in documents:
        generate(doc)


# generate tests for projects in the given paths - used for the experiments
for i in range(0, len(paths)):

    documents = process_file(paths[i])

    class_name = "insert_class_name"
    attribute_version = "insert_attribute_version"
    class_version = "insert_class_version"

    # create file
    # if exists, appends existing file
    f = open("generated_code/generated_steps_" + str(i) + ".py", "a+")

    f.write("from behave import * \n")

    f.write("\n")

    for doc in documents:
        generate(doc)

# get a list of sentences in a paragraph
def get_paragraph(paragraph):
    paragraph_sentences = {}

    sentences = paragraph.split("\n")

    scenario = sentences[0].strip()
    if '@' in scenario:
        sentences = sentences[1:]
    steps = []

    for i in range(1, len(sentences)):
        steps += [sentences[i].strip()]

    paragraph_sentences[scenario] = steps

    return paragraph_sentences


# extract a scenario and the scenario sentences (Given, When, Then) from a feature file
def process_file(path):
    feature_file = open(path)

    data = feature_file.read()

    # print(data)

    all_paragraphs = data.split("\n\n")

    # print paragraphs

    paragraphs = []

    for paragraph in all_paragraphs:
        tempo = paragraph
        first_word = tempo.split(":")
        if first_word[0].strip() == "Scenario" or first_word[0].strip() == "Scenario Outline":
            paragraphs += [paragraph]
        splitcheck = first_word[0].strip().split("\n")
        if '@' in splitcheck[0].strip(): #check if starts with a tag
            if splitcheck[1].strip() == "Scenario" or splitcheck[1].strip() == "Scenario Outline":
                paragraphs += [paragraph]


    documents = []

    for paragraph in paragraphs:
        final_paragraphs = get_paragraph(paragraph)
        scenarios = final_paragraphs.keys()
        for scenario in scenarios:
            steps = final_paragraphs[scenario]
            for step in steps:
                documents += [step.strip()]
    return documents

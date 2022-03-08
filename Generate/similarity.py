import spacy
nlp = spacy.load('en_core_web_md')

original_files = ["Banking/features/steps/steps.py",
                  "/home/ruxi/experiment_repos/behave-demo/features/steps/steps_218.py",
                  "/home/ruxi/experiment_repos/behave-restful/features/steps/steps_220.py",
                  "/home/ruxi/experiment_repos/behave_web2/features/steps/steps_225.py",
                  "/home/ruxi/experiment_repos/cucumber-python/features/steps/steps_28.py",
                  "/home/ruxi/experiment_repos/DataSetVerification/features/steps/steps_35.py",
                  "/home/ruxi/experiment_repos/Gherkin-Demos-python/test/features/steps/steps_58.py",
                  "/home/ruxi/experiment_repos/python-testing-examples/features/steps/steps_126.py",
                  "/home/ruxi/experiment_repos/vending-machine/features/steps/steps_181.py",
                  "/home/ruxi/experiment_repos/vending-machine/features/steps/steps_182.py",
                  "/home/ruxi/experiment_repos/vending-machine/features/steps/steps_183.py"
                  ]
generated_files = ["whitebox_generated_steps_SRL/generated_steps_0.py",
                   "whitebox_generated_steps_SRL/generated_steps_1.py",
                   "whitebox_generated_steps_SRL/generated_steps_2.py",
                   "whitebox_generated_steps_SRL/generated_steps_3.py",
                   "whitebox_generated_steps_SRL/generated_steps_4.py",
                   "whitebox_generated_steps_SRL/generated_steps_5.py",
                   "whitebox_generated_steps_SRL/generated_steps_6.py",
                   "whitebox_generated_steps_SRL/generated_steps_7.py",
                   "whitebox_generated_steps_SRL/generated_steps_8.py",
                   "whitebox_generated_steps_SRL/generated_steps_9.py",
                   "whitebox_generated_steps_SRL/generated_steps_10.py"]
def get_file_contents(filename):
  with open(filename, 'r') as filehandle:
    filecontent = filehandle.read()
    return (filecontent)

def similarity(file1, file2):
    f_doc1 = get_file_contents(file1)
    f_doc2 = get_file_contents(file2)

    doc1 = nlp(f_doc1)
    doc2 = nlp(f_doc2)

    return doc1.similarity(doc2)

file1 = "generated_steps.py"
file2 = "Banking/features/steps/steps.py"

for i in range (0,len(original_files)):
    print (similarity(original_files[i],generated_files[i]))

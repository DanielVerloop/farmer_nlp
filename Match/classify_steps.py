import inspect
import random
import nltk
from projects import modules


# print(inspect.getmembers(getattr(steps,'BankAccount'),inspect.ismethod))

labeled_steps = []
featuresets = []

# feature extractor
def step_features(module, step):

    lines = inspect.getsourcelines(getattr(module,step))
    classes = get_module_classes(module)
    functions = get_module_functions(module)

    constructor_call = False
    method_call = False
    assertion = False

    for line in lines[0]:
        # check if there is a constructor call and assignment to function argument
        for class_name in classes:
            if class_name in line:
                for function_argument in functions[step]:
                    if function_argument in line:
                        constructor_call = True

        # check if there us a method call
        for function_argument in functions[step]:
            if function_argument in line:
                #for class_name in classes:
                 #   for method_name in classes[class_name]:
                        if "." in line:#+ method_name in line:
                            method_call = True

        # check if there is an assertion
        if 'assert' in line:
            assertion = True

    return {'constructor_call':constructor_call,'method_call':method_call, 'assertion':assertion}

# get all external classes and methods used in a steps5.py file, e.g. BankAccount, BankAccount.withdraw
def get_module_classes(module):
    classes = {}

    for class_name, class_data in inspect.getmembers(module, inspect.isclass):
        if class_name == '__builtins__':
            continue
        classes[class_name] = []
        for method_name,method_data in inspect.getmembers(getattr(module,class_name), inspect.ismethod):
            classes[class_name]+=[method_name]
    return classes

# get all step implementations in a step.py file + the arguments of each function
def get_module_functions(module):
    functions = {}

    for function_name,function_data in inspect.getmembers(module, inspect.isfunction):
        if function_name == '__builtins__':
            continue
        function_source_lines = inspect.getsourcelines(getattr(module, function_name))
        if (function_source_lines[0][0][:1] == '@'):
            functions[function_name]=inspect.getfullargspec(getattr(module,function_name)).args
    return functions

# build feature set and label steps
count = 0
count_wrong = 0
assumed_right = 0
for module in modules:
    for name,data in inspect.getmembers(module, inspect.isfunction):
        if name == '__builtins__':
            continue
        lines = inspect.getsourcelines(getattr(module, name))
        source = inspect.getsource((getattr(module,name)))

        #if ("pass" not in source):
        #if "raise" not in source:
        #if "print" not in source:
        if "pass" not in source:
            if "NotImplementedError" not in source:
                if "print" not in source:
                    if (lines[0][0][:1] == '@'):
                        if (lines[0][0][:2] == '@g'):
                #print name
                            if "assert" not in source:
                                assumed_right+=1
                                feats = step_features(module, name)
                                if feats['constructor_call'] is True and feats['assertion'] is False:
                                    labeled_steps += [(name + "_" + str(count), 'given')]
                                    featuresets +=[(step_features(module,name),'given')]
                                else:
                                    print (source)
                                    count_wrong+=1
                        elif (lines[0][0][:2] == '@w'):
                            feats = step_features(module, name)
                            if "assert" not in source and feats['constructor_call'] is False:
                                assumed_right += 1
                #print name
                #if constr == False:
                                if feats['method_call'] is True and feats['assertion'] is False:
                                    labeled_steps += [(name + "_" + str(count),'when')]
                                    featuresets += [(step_features(module,name),'when')]
                                else:
                                    print (source)
                                    count_wrong+=1
                    elif (lines[0][0][:2] == '@t'):
                #print name
                #if constr == False:
                            feats = step_features(module, name)
                            if feats['constructor_call'] is False:
                                assumed_right += 1
                                if feats['constructor_call'] is False and feats['assertion'] is True:
                                    labeled_steps += [(name + "_" + str(count),'then')]
                                    featuresets += [(step_features(module,name),'then')]
                                else:
                                    print (source)
                                    count_wrong+=1


# classify

#for feature in featuresets:
 #   print (feature)

print (len(featuresets))

random.shuffle(featuresets)
train_set = featuresets[:100]

test_set = featuresets[100:]

#random.shuffle(test_set)

classifier = nltk.NaiveBayesClassifier.train(train_set)

print (nltk.classify.accuracy(classifier,test_set))

classifier.show_most_informative_features(5)

print (count_wrong)
print (assumed_right)
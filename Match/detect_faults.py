import inspect
import random
import nltk
from projects import modules


#print inspect.getmembers(getattr(steps,'BankAccount'),inspect.ismethod)

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
file_op = 0
os_op = 0
dir_op = 0
web = 0
web_given = 0
web_when = 0
execute_other_steps = 0

def get_all_members(module):

    members = []

    for name,data in inspect.getmembers(module):
        members += [name]

    return members

for module in modules:
    for name,data in inspect.getmembers(module, inspect.isfunction):
        if name == '__builtins__':
            continue
        lines = inspect.getsourcelines(getattr(module, name))
        source = inspect.getsource((getattr(module,name)))

        members = get_all_members(module)

        no_pass = False
        not_impl_err = False
        only_print = False

        given_asrt = False
        when_asrt = False
        suitable= False

        if (lines[0][0][:1] == '@'):
            if (lines[0][0][:2] == '@g'):
                if 'webdriver' in members:
                    web_given += 1
            if (lines[0][0][:2] == '@w'):
                if 'webdriver' in members:
                    web_when += 1
            if "  pass" not in source:
                no_pass = True
                if "NotImplementedError" not in source:
                    not_impl_err = True
                    if "print" not in source:
                        only_print = True
                        if (lines[0][0][:2] == '@g'):
                            feats = step_features(module, name)
                            if "assert" in source:
                                given_asrt = True
                            if feats['constructor_call'] is True and feats['assertion'] is False:
                                labeled_steps += [(name + "_" + str(count), 'given')]
                                featuresets +=[(step_features(module,name),'given')]
                                suitable = True
                                count+=1
                            #else:
                            #    print (source)
                        elif (lines[0][0][:2] == '@w'):
                            feats = step_features(module, name)
                            if "assert" in source:
                                when_asrt = True
                            if feats["constructor_call"] is False and feats['method_call'] is True and feats['assertion'] is False:
                                labeled_steps += [(name + "_" + str(count),'when')]
                                featuresets += [(step_features(module,name),'when')]
                                suitable = True
                                count += 1
                            #else:
                                #print (source)
                        elif (lines[0][0][:2] == '@t'):
                            feats = step_features(module, name)
                            if feats['constructor_call'] is False and feats['assertion'] is True:
                                labeled_steps += [(name + "_" + str(count),'then')]
                                featuresets += [(step_features(module,name),'then')]
                                suitable = True
                                count += 1
                            #else:
                                #print (source)
        #else:
         #   print (source)
            if no_pass is True and not_impl_err is True and only_print is True and suitable is False:
                if "@given" in source and "assert" not in source: # or (lines[0][0][:2] == '@w' and when_asrt is True):
                    count_wrong+= 1
                    print (source)
                    if "file" in source:
                        file_op += 1
                    if "os." in source:
                        os_op += 1
                    if "dir" in source:
                        dir_op += 1
                    if "browser" in source:
                        web += 1
                    if "execute_steps" in source:
                        execute_other_steps += 1
                elif "@when" in source and "assert" not in source:
                    feats = step_features(module, name)
                    if feats['constructor_call'] is False:
                        print (source)
                        count_wrong += 1
                        if "file" in source:
                            file_op += 1
                        if "os." in source:
                            os_op += 1
                        if "dir" in source:
                            dir_op += 1
                        if "browser" in source:
                            web += 1
                        if "execute_steps" in source:
                            execute_other_steps += 1
                elif "@then" in source:
                    feats = step_features(module, name)
                    if feats['constructor_call'] is False:
                        print (source)
                        count_wrong += 1
                    if "file" in source:
                        file_op += 1
                    if "os." in source:
                        os_op += 1
                    if "dir" in source:
                        dir_op += 1
                    if "browser" in source:
                        web += 1
                    if "execute_steps" in source:
                        execute_other_steps += 1



# classify

#for feature in featuresets:
 #   print (feature)
#print (labeled_steps)
print (len(featuresets))

print (count_wrong)

accuracies = 0
for i in range (0,10):
    random.shuffle(featuresets)
    train_set = featuresets[:100]

    test_set = featuresets[100:]

#random.shuffle(test_set)

    classifier = nltk.NaiveBayesClassifier.train(train_set)

    accuracies+= nltk.classify.accuracy(classifier,test_set)

    classifier.show_most_informative_features(5)

print (accuracies/10.0)

print ("File: ",file_op)
print ("Os: ", os_op)
print ("Dir: ", dir_op)
print ("Execute other steps: ", execute_other_steps)
print ("Web: ", web)

print ("#############")

print ("no. of given steps using selenium webdriver",web_given)
print ("no. of when steps using selenium webdriver",web_when)
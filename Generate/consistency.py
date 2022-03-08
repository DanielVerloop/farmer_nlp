import inspect


# extract information to be used to compare if generated API matches project API


# get all class names in a step.py file
def get_module_classes(module):
    classes = {}

    for class_name, class_data in inspect.getmembers(module, inspect.isclass):
        if class_name == '__builtins__':
            continue
        classes[class_name] = []
        for method_name, method_data in inspect.getmembers(getattr(module, class_name), inspect.ismethod):
            classes[class_name] += [method_name]
    return classes


# get all step implementations in a step.py file + the arguments of each function
def get_module_functions(module):
    functions = {}

    for function_name, function_data in inspect.getmembers(module, inspect.isfunction):
        if function_name == '__builtins__':
            continue
        function_source_lines = inspect.getsourcelines(getattr(module, function_name))
        if function_source_lines[0][0][:1] == '@':
            functions[function_name] = inspect.getfullargspec(getattr(module, function_name)).args
    return functions

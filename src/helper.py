import re


def inline_arg_compile(args):
    """
    Using regex to load inline arguments.
    Arguments:
    ------
    `args` (string): '--func(condition, input)' or '--func' or combined

    Output:
    ------
    dictionary: `{'func_name': {'condition': function_condition, 'input': input}}`
    """
    # initiate
    output = {}

    # acceptance inputs criteria
    condition1 = (args != '') & (args[0:2] == '--')  # correct syntax args
    condition2 = args in ['', 'nan']  # empty input

    assert (condition1 | condition2), "Usage: '--func' or '--func(condition, input)' "
    ### Syntax to compile ###
    syntax = r'--(?P<func>\w+)(\((?P<condition>\w*)(,(?P<input>\w*))?\))?'

    match = re.finditer(syntax, args)
    match_list = [n.groupdict() for n in match]

    ### Reshape list to dict ###
    for item in match_list:
        func_name = item['func']
        output[func_name] = {
            'condition': item['condition'],
            'input': item['input']
        }

    return output


# print(inline_arg_compile('--match'))
# print(inline_arg_compile('--match(5,hi)'))
# print(inline_arg_compile('--match(1)'))

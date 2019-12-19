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

    # acceptance criteria
    condition1 = (args != '') & (args[0:2] == '--')  # correct syntax args
    condition2 = args in ['', 'nan']  # empty imput

    assert (condition1 | condition2), "Usage: '--func' or '--func(condition, input)' "
    match = re.finditer(
        r'--(?P<func>\w+)(?:\((?P<condition>.*),(?P<input>.*)\))?', args)
    match_list = [n.groupdict() for n in match]

    # form dictionary
    for item in match_list:
        func_name = item['func']
        output[func_name] = {
            'condition': item['condition'],
            'input': item['input']
        }

    return output

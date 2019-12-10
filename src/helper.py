import re


def inline_arg(args):
    """
    Using regex to load inline arguments.
    Arguments:
    ------
    `args` (string): '--func(condition, output)' or '--func' or combined

    Output:
    ------
    list: `[{args_dict1}, {args_dict2}]`
    """
    # acceptance criteria
    condition1 = (args != '') & (args[0:2] == '--')  # correct syntax arhs
    condition2 = args == ''  # empty imput
    assert (condition1 | condition2), "Usage: '--func' or '--func(condition, output)' "
    match = re.finditer(
        r'--(?P<func>\w+)(?:\((?P<condition>.*),(?P<output>.*)\))?', args)
    return [n.groupdict() for n in match]

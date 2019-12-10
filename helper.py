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
    assert (args[0:2] == '--'), "Usage: '--func' or '--func(condition, output)'"
    match = re.finditer(
        r'--(?P<func>\w+)(?:\((?P<condition>.*),(?P<output>.*)\))?', args)
    return [n.groupdict() for n in match]

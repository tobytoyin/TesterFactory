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

    assert condition1 | condition2, "Usage: '--func' or '--func(condition, input)' "
    ### Syntax to compile ###
    syntax = r'--(?P<func>\w+)(\((?P<condition>\w*)(,\s?(?P<input>\w*))?\))?'

    match = re.finditer(syntax, args)
    match_list = [n.groupdict() for n in match]

    ### Reshape list to dict ###
    for item in match_list:
        func_name = item['func']
        output[func_name] = {'condition': item['condition'], 'input': item['input']}

    return output


def print_table(input_dict, title='', header=('Key', 'Value'), style=('', '-')):
    """Print the dict in a table form"""
    assert input_dict.__class__ is dict, "Only accept class='dict'"
    if input_dict is None:
        return None

    max_string = 110
    key_list = list(input_dict.keys())
    val_list = list(map(str, input_dict.values()))
    key_list.append(header[0])
    val_list.append(header[1])

    # find the longest key value
    width_left = min(len(max(key_list, key=len)), max_string)
    width_right = min(len(max(val_list, key=len)), max_string)
    width_full = width_left + width_right + 2 + 2 + 1

    # structure
    table_struct = f"{{:>{width_left}}} | {{:>{width_right}}}"

    # top border
    print(style[0] * width_full)

    # title
    print(f"{{:^{width_full}}}".format(f"~{title}~"))
    print(style[1] * width_full)

    # contents
    print(table_struct.format(header[0], header[1]))
    print(style[1] * width_full)
    for key, val in input_dict.items():
        # format empty value
        if val == '':
            val = '-'

        # trim long string
        if len(str(val)) > max_string:
            print(table_struct.format(key, str(val)[0:max_string]))
        else:
            print(table_struct.format(key, str(val)))

    # bot boader
    print(style[0] * width_full)
    print("\n")


# print(inline_arg_compile('--match'))
# print(inline_arg_compile('--match(5,hi)'))
# print(inline_arg_compile('--match(1)'))

# dic = {'tc': '001', 'field1': 5, 'field2': '456'}
# print_table(dic, title='testing', style=('=', '-', ''))

from tokenize import tokenize, INDENT, DEDENT, NL, NEWLINE
from typing import List
from pipe_fn import e
from linq.standard.general import Map, Skip


def handle_eps(x):
    if x is '':
        return '$'

    return x


def handle_indent(seq):
    get_nl = False
    for item in seq:
        if item.type is INDENT:
            yield '\n' + (' ' * item.end[1])
        elif item.type is DEDENT:
            yield '\n' + (' ' * item.start[1])
        elif item.type is NL or item.type is NEWLINE:
            get_nl = True
        else:
            if get_nl:
                yield '\n' + (' ' * item.start[1])
                get_nl = False
            yield item.string


def word_stream(lines: List[str]):
    return lines | e / Map @ str.encode | \
                   e / getattr @ '__next__' | \
                   e / tokenize | e / Skip @ 1 | \
                   e / handle_indent


def token(src):
    return src | e / str.split | e / word_stream | e / list

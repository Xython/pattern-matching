
import re
from tokenize import tokenize, TokenInfo
from typing import List
from pipe_fn import e
from linq.standard.general import Map, Skip


def handle_eps(x):
    if x is '':
        return '$'

    return x


def word_stream(lines: List[str]):
    return lines | e / Map @ str.encode | e / getattr @ '__next__' | e / tokenize | e / Skip @ 1 | e / Map @ (
        lambda x: x.string) | e / Map @ handle_eps


def token(src):
    return src | e / str.split | e / word_stream | e / list


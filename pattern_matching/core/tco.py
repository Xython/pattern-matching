import types
from collections import namedtuple
from inspect import getsourcelines

from Ruikowa.Bootstrap.Ast import Ast
from Ruikowa.ObjectRegex.MetaInfo import MetaInfo
from pipe_fn import e

from .parserlib.call_parser import Stmts
from .parserlib.utoken import word_stream

from Ruikowa.ErrorFamily import handle_error

parser = handle_error(Stmts)

__MarkReturn__ = 0
__MarkTCO__ = 1

tc_stack = namedtuple('tc_stack', ['args', 'kwargs'])  # for tco


def __hold_tc_stack__(*args, **kwargs):
    return tc_stack(args, kwargs)


def generate_session(fn_name):
    can_opt_next = False

    def generate_opt_codes(ast):
        nonlocal can_opt_next

        if isinstance(ast, str):

            if ast == 'return':
                return 'yield __MarkReturn__,'.format(fn_name)
            elif ast == 'yield':
                raise SyntaxError(
                    "TCO functions cannot support `yield` streams, please generate streams in functional style!")
            else:

                return ast

        elif ast.name == 'Stmts':
            return ' '.join(map(generate_opt_codes, ast))

        elif ast.name == 'Expr':
            if isinstance(ast[0], Ast) and ast[0].name == 'Call':
                return generate_opt_codes(ast[0])
            else:
                return ' '.join(map(generate_opt_codes, ast))
        elif ast.name == 'Call':
            expr = ast[0]
            if isinstance(expr[0], str) and expr[0] == fn_name and len(expr) is 1:
                if can_opt_next:
                    expr[0] = '__hold_tc_stack__'
                    return ' (yield __MarkTCO__, {})'.format(' '.join(map(generate_opt_codes, ast)))
                else:
                    expr[0] = '_'
                    can_opt_next = True
            return ' '.join(map(generate_opt_codes, ast))
        else:
            raise TypeError('invalid ast type')

    return generate_opt_codes


def handle_indent(x, min_indent):
    return x[min_indent:]


def refactor(scope, func, pattern=None):
    """
    I don't have enough time to look up how to add `lineno` or `co_firstlineno` efficiently.
    Appreciate a lot if you could help me with refactoring the functions.
    """

    if '__MarkReturn__' not in scope or '__MarkTCO__' not in scope or '__hold_tc_stack__' not in scope:
        scope['__MarkReturn__'] = __MarkReturn__
        scope['__MarkTCO__'] = __MarkTCO__
        scope['__hold_tc_stack__'] = __hold_tc_stack__
    fn_name = func.__name__
    src = getsourcelines(func)[0][1:]
    words = src | e / word_stream | e / list
    ast = parser(words, meta=MetaInfo(), partial=False)
    new_codes = f'if True:\n{generate_session(fn_name)(ast)}'

    codes = compile(new_codes, func.__code__.co_filename, 'exec')
    exec(codes, scope)
    new_func = scope['_']
    function_type_sign = f'{func.__name__}/{",".join(map(str, pattern[0]))}{pattern[1] if len(pattern) is 2 else ""}'

    codes = types.CodeType(
        new_func.__code__.co_argcount,
        new_func.__code__.co_kwonlyargcount,
        new_func.__code__.co_nlocals,
        new_func.__code__.co_stacksize,
        new_func.__code__.co_flags,
        new_func.__code__.co_code,
        new_func.__code__.co_consts,
        new_func.__code__.co_names,
        new_func.__code__.co_varnames,
        func.__code__.co_filename,
        function_type_sign,
        func.__code__.co_firstlineno,
        func.__code__.co_lnotab,
        func.__code__.co_freevars,
        func.__code__.co_cellvars)

    args = (codes,
            scope,
            function_type_sign,
            func.__defaults__,
            func.__closure__)
    return types.FunctionType(*args)

    # codes = compile(new_codes, _file, 'exec')
    # exec(codes, scope)
    # func = scope['_']


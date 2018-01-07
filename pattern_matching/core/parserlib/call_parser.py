
from Ruikowa.ObjectRegex.Node import Ref, AstParser, SeqParser, LiteralParser, CharParser, MetaInfo, DependentAstParser
try:
    from .etoken import token
except:
    from etoken import token
import re
namespace     = globals()
recurSearcher = set()
Any = LiteralParser('[^\(\)\.]*', name = 'Any', isRegex = True)
Expr = AstParser([Ref('Call')],[Ref('Any'),SeqParser([LiteralParser('.', name='\'.\''),Ref('Any')])], name = 'Expr')
Call = AstParser([Ref('Expr'),LiteralParser('(', name='\'(\''),SeqParser([Ref('Expr')]),SeqParser([LiteralParser(')', name='\')\'')])], name = 'Call')
Stmts = AstParser([SeqParser([Ref('Expr')])], name = 'Stmts')
Expr.compile(namespace, recurSearcher)
Call.compile(namespace, recurSearcher)
Stmts.compile(namespace, recurSearcher)

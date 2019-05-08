# Copyright 2019 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0

import ast
import pickle
import pickletools
from contextlib import suppress
from functools import wraps
from itertools import chain, takewhile
from typing import TypeVar, Iterable, Tuple

from hissp.munger import munge, demunge

SLASH = munge("/")
LAMBDA = munge("\\")
STAR = munge("*")
STARS = STAR * 2
AND = munge("&")
BLANK = munge("?")

MACRO = munge("!.")
SMACRO = SLASH + MACRO

# repr() always reverses.
REPR = frozenset({type(None), bool, bytes, str})
# Needs (), and some invalid reprs, like 'nan'
BASIC = frozenset({int, float, complex})


class CompileError(SyntaxError):
    pass


def trace(method):
    @wraps(method)
    def tracer(self, form):
        try:
            return method(self, form)
        except CompileError as e:
            e.msg = f"\n{method.__name__}:\n{form!r}" + e.msg
            raise e
        except Exception as e:
            raise CompileError(f"\n{method.__name__}:\n{form!r}") from e

    return tracer


class Compiler:
    """
    The Hissp compiler.
    """

    def __init__(self, ns=None, evaluate=True):
        self.ns = ns or {"__name__": "<compiler>", BLANK: {}}
        self.evaluate = evaluate

    def compile(self, forms: Iterable) -> str:
        result = []
        for form in forms:
            form = self.form(form)
            self.eval(form)
            result.append(form)
        return "\n\n".join(result)

    def eval(self, form):
        if not self.evaluate:
            return
        try:
            eval(compile(form, "<Hissp>", "eval"), self.ns)
        except Exception as e:
            raise CompileError("\n" + form) from e

    def form(self, form) -> str:
        """
        Translate Hissp form to the equivalent Python code as a string.
        """
        if type(form) is tuple and form:
            return self.tuple(form)
        if type(form) is str:
            return self.symbol(form)
        return self.quoted(form)

    def tuple(self, form: tuple) -> str:
        """Calls, macros, special forms."""
        head, *tail = form
        if type(head) is str:
            head = self.alias(head)
            if head == "quote":
                if len(form) != 2:
                    raise SyntaxError
                return self.quoted(form[1])
            if head == LAMBDA:
                return self.fn(form)
            if SMACRO in head or head.startswith(MACRO):
                return self.macro(head, tail)
        return self.call(form)

    def quoted(self, form) -> str:
        """Compile forms that evaluate to themselves."""
        case = type(form)
        if case is list:
            return f"[{self._elements(form)}]"
        if case is set:
            return f"""{{{self._elements(form) or "*''"}}}"""
        if case is tuple:
            return f"({self._elements(form)},)" if form else "()"
        if case is dict:
            return "{%s}" % ",".join(
                f"{self.quoted(k)}:{self.quoted(v)}" for k, v in form.items()
            )
        if case in REPR:  # reversible reprs
            return repr(form)
        if case in BASIC:
            with suppress(ValueError):  # Some repr()s don't round-trip.
                return self.basic(form)
        return self.pickle(form)

    def _elements(self, form) -> str:
        return ",".join(map(self.quoted, form))

    def basic(self, form) -> str:
        result = f"({repr(form)})"  # Need (). E.g. (1).real
        ast.literal_eval(result)  # Does it round-trip?
        return result

    @trace
    def pickle(self, form) -> str:
        """The final fallback for self.quoted()."""
        dumps = pickletools.optimize(pickle.dumps(form, -1))
        return f"__import__('pickle').loads(  # {form!r}\n{dumps})"

    def fn(self, form: tuple) -> str:
        r"""
        Function definition special form.

        (\ (<parameters>)
          <body>)

        The parameters tuple is divided into (<single> & <paired>)

        Parameter types are the same as Python's.
        For example,
        >>> transpile(
        ... (LAMBDA, ('a','b',
        ...         AND, 'e',1, 'f',2,
        ...         STAR,'args', 'h',4, 'i',BLANK, 'j',1,
        ...         STARS,'kwargs',),
        ...   42,),
        ... )
        '(lambda a,b,e=(1),f=(2),*args,h=(4),i,j=(1),**kwargs:(42))'

        The special names * and ** designate the remainder of the
        positional and keyword parameters, respectively.
        Note this body has an implicit PROGN.
        >>> transpile(
        ... (LAMBDA, (AND,STAR,'args',STARS,'kwargs',),
        ...   ('print','args',),
        ...   ('print','kwargs',),),
        ... )
        '(lambda *args,**kwargs:(print(args),print(kwargs))[-1])'

        You can omit the right of a pair with ? (except the final **kwargs).
        Also note that the body can be empty.
        >>> transpile(
        ... (LAMBDA, (AND,'a',1, STAR,BLANK, 'b',BLANK, 'c',2,),),
        ... )
        '(lambda a=(1),*,b,c=(2):())'

        The '&' may be omitted if there are no paired parameters.
        >>> transpile((LAMBDA, ('a','b','c',AND,),),)
        '(lambda a,b,c:())'
        >>> transpile((LAMBDA, ('a','b','c',),),)
        '(lambda a,b,c:())'
        >>> transpile((LAMBDA, (AND,),),)
        '(lambda :())'
        >>> transpile((LAMBDA, (),),)
        '(lambda :())'

        & is required if there are any paired parameters, even if there
        are no single parameters.
        >>> transpile((LAMBDA, (AND,STARS,'kwargs',),),)
        '(lambda **kwargs:())'
        """
        fn, parameters, *body = form
        assert fn == LAMBDA
        return f"(lambda {','.join(self.parameters(parameters))}:{self.body(body)})"

    @trace
    def parameters(self, parameters: tuple) -> Iterable[str]:
        parameters = iter(parameters)
        yield from takewhile(lambda a: a != AND, parameters)
        for k, v in pairs(parameters):
            if k == STAR:
                yield "*" if v == BLANK else f"*{v}"
            elif k == STARS:
                yield f"**{v}"
            elif v == BLANK:
                yield k
            else:
                yield f"{k}={self.form(v)}"

    @trace
    def body(self, body: list) -> str:
        if len(body) > 1:
            return f"({','.join(map(self.form, body))})[-1]"
        if not body:
            return "()"
        return self.form(body[0])

    def macro(self, head: str, tail: tuple) -> str:
        expansion = f"{self.symbol(head)}({(','.join(map(self.quoted, tail)))})"
        try:
            expansion = eval(compile(expansion, f"<macro {head}>", "eval"), self.ns)
        except Exception as e:
            raise CompileError(f"\nexpand:\n{expansion}") from e
        return self.form(expansion)

    @trace
    def call(self, form: tuple) -> str:
        r"""
        Call form.

        Any tuple that is not quoted, empty, or a special form or macro is
        a call.

        Like Python, it has three parts.
        (<callable> <args> & <kwargs>)
        For example,
        >>> transpile(
        ... ('print',1,2,3,AND,'sep',('quote',":",), 'end',('quote',"\n\n",),)
        ... )
        "print((1),(2),(3),sep=':',end='\\n\\n')"

        Either <args> or <kwargs> may be empty.
        >>> transpile(('foo',AND,),)
        'foo()'
        >>> transpile(('foo','bar',AND,),)
        'foo(bar)'
        >>> transpile(('foo',AND,'bar','baz',),)
        'foo(bar=baz)'

        The & is optional if the <kwargs> part is empty.
        >>> transpile(('foo',),)
        'foo()'
        >>> transpile(('foo','bar',),)
        'foo(bar)'

        The <kwargs> part has implicit pairs; there must be an even number.

        Use the special keywords * and ** for iterable and mapping unpacking
        >>> transpile(
        ... ('print',AND,STAR,[1,2], 'a',3, STAR,[4], STARS,{'sep':':','end':'\n\n'},),
        ... )
        "print(*([(1),(2)]),a=(3),*([(4)]),**({'sep':':','end':'\\n\\n'}))"

        Unlike other keywords, these can be repeated, but a '*' is not
        allowed to follow '**', as in Python.

        Method calls are similar to function calls.
        (.<method name> <object> <args> & <kwargs>)
        Like Clojure, a method on the first object is assumed if the
        function name starts with a dot.
        >>> transpile(('.conjugate', 1j,),)
        '(1j).conjugate()'
        >>> eval(_)
        -1j
        >>> transpile(('.decode', b'\xfffoo', AND, 'errors',('quote','ignore',),),)
        "b'\\xfffoo'.decode(errors='ignore')"
        >>> eval(_)
        'foo'
        """
        form = iter(form)
        head = next(form)
        args = chain(
            map(self.form, takewhile(lambda a: a != AND, form)),
            (
                f"{demunge(k)}({self.form(v)})"
                if k in {STAR, STARS}
                else f"{k}={self.form(v)}"
                for k, v in pairs(form)
            ),
        )
        if type(head) is str and head.startswith("."):
            return f"{next(args)}.{head[1:]}({','.join(args)})"
        return f"{self.form(head)}({','.join(args)})"

    @trace
    def symbol(self, symbol: str) -> str:
        symbol = self.alias(symbol)
        if SLASH in symbol and not symbol.startswith(SLASH):
            parts = symbol.split(SLASH, 1)
            return "__import__({0!r}{fromlist}).{1}".format(
                parts[0], parts[1], fromlist=",fromlist='?'" if "." in parts[0] else ""
            )
        return symbol

    def alias(self, symbol: str) -> str:
        return self.ns[BLANK].get(symbol, symbol)


T = TypeVar("T")


def pairs(it: Iterable[T]) -> Iterable[Tuple[T, T]]:
    it = iter(it)
    for k in it:
        yield k, next(it)


def transpile(form):
    return Compiler(evaluate=False).compile([form])

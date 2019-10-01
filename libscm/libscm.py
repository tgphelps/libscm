
from typing import Any, List

Symbol = str


class UnboundError(Exception):
    pass


class Env(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."
    def __init__(self, parms=(), args=(), outer=None):
        self.update(list(zip(parms, args)))
        self.outer = outer
        self.err_handler = None

    def find(self, var):
        "Find the innermost Env where var appears."
        # return self if var in self else self.outer.find(var)
        while True:
            if var in self:
                return self
            else:
                if self.outer:
                    self.outer.find(var)
                else:
                    if self.err_handler:
                        self.err_handler(var)  # Fix the error or abort
                        self.find(var)
                    else:
                        raise UnboundError(var)

    def set_err_handler(self, func):
        self.err_handler = func


def add_globals(env: Env) -> Env:
    "Add some Scheme standard procedures to an environment."
    import math
    import operator as op
    env.update(vars(math))  # sin, sqrt, ...
    # XXX Should remove some __*__ vars that aren't math functions

    env.update(
     {'+': op.add, '-': op.sub, '*': op.mul, '/': op.truediv, 'not': op.not_,
      '>': op.gt, '<': op.lt, '>=': op.ge, '<=': op.le, '=': op.eq,
      'equal?': op.eq, 'eq?': op.is_, 'length': len, 'append': op.add,
      'cons': lambda x, y: [x]+y,
      'car': lambda x: x[0],
      'cdr': lambda x: x[1:],
      'list': lambda *x: list(x),
      'list?': lambda x: isa(x, list),
      'null?': lambda x: x == [],
      'symbol?': lambda x: isa(x, Symbol)})
    return env


def handle_it(var):
    "Handle an unbound 'var' error. Just abort."
    # print(f"Var '{var}' unbound")
    raise UnboundError(var)


global_env = add_globals(Env())
# global_env.set_err_handler(handle_it)


def add_global_var(var: str, val: Any) -> None:
    global_env[var] = val


def set_err_handler(func):
    global_env.set_err_handler(func)

isa = isinstance


def eval(x, env=global_env) -> Any:
    "Evaluate an expression in an environment."
    if isa(x, Symbol):             # variable reference
        return env.find(x)[x]
    elif not isa(x, list):         # constant literal
        return x
    elif x[0] == 'quote':          # (quote exp)
        (_, exp) = x
        return exp
    elif x[0] == 'if':             # (if test conseq alt)
        (_, test, conseq, alt) = x
        return eval((conseq if eval(test, env) else alt), env)
    elif x[0] == 'set!':           # (set! var exp)
        (_, var, exp) = x
        env.find(var)[var] = eval(exp, env)
    elif x[0] == 'define':         # (define var exp)
        (_, var, exp) = x
        env[var] = eval(exp, env)
    elif x[0] == 'lambda':         # (lambda (var*) exp)
        (_, vars, exp) = x
        return lambda *args: eval(exp, Env(vars, args, env))
    elif x[0] == 'begin':          # (begin exp*)
        for exp in x[1:]:
            val = eval(exp, env)
        return val
    else:                          # (proc exp*)
        exps = [eval(exp, env) for exp in x]
        proc = exps.pop(0)
        return proc(*exps)

# parse, read, and user interaction


def parse(s: str) -> Any:
    "Read a Scheme expression from a string."
    return read_expr(tokenize(s))


def tokenize(s: str) -> List[str]:
    "Convert a string into a list of tokens."
    tokens = s.replace('(', ' ( ').replace(')', ' ) ').split()
    # print(f'Tokens: {tokens}')
    return tokens


def read_expr(tokens: List[str]) -> Any:
    "Read an expression from a sequence of tokens."
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while reading')
    token = tokens.pop(0)
    if token == '(':
        L = []
        while tokens[0] != ')':
            L.append(read_expr(tokens))
        tokens.pop(0)  # pop off ')'
        return L
    elif token == ')':
        raise SyntaxError('unexpected )')
    else:
        return atom(token)


def atom(token: str) -> Any:
    "Numbers become numbers; every other token is a symbol."
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)


def to_string(exp: str) -> str:
    "Convert a Python object back into a Lisp-readable string."
    return '(' + ' '.join(map(to_string, exp)) + ')' \
           if isa(exp, list) else str(exp)


def main(prompt='lis.py> ') -> None:
    "A prompt-read-eval-print loop."
    while True:
        try:
            s = input(prompt)
        except EOFError:
            break
        tokens = tokenize(s)
        # expr = parse(s)

        while len(tokens) > 0:
            expr = read_expr(tokens)
            # print('expr =', expr)
            # print('left =', tokens)
            val = eval(expr)
            if val is not None:
                print(to_string(val))


if __name__ == '__main__':
    main()

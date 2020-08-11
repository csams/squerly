"""
The boolean module lets you create complicated boolean expressions by
composing objects. They can then be evaluated against multiple values.
"""
import logging
import operator
import re

from functools import partial, wraps

log = logging.getLogger(__name__)

__all__ = [
    "pred",
    "flip",
    "TRUE",
    "FALSE",
    "lt",
    "le",
    "eq",
    "ge",
    "gt",
    "isin",
    "contains",
    "search",
    "matches",
    "startswith",
    "endswith",
]


class Boolean:
    def test(self, value):
        raise NotImplementedError()

    def __and__(self, other):
        return All(self, other)

    def __or__(self, other):
        return Any(self, other)

    def __invert__(self):
        return Not(self)


class Any(Boolean):
    def __init__(self, *predicates):
        self.predicates = predicates

    def test(self, value):
        return any(predicate.test(value) for predicate in self.predicates)


class All(Boolean):
    def __init__(self, *predicates):
        self.predicates = predicates

    def test(self, value):
        return all(predicate.test(value) for predicate in self.predicates)


class Not(Boolean):
    def __init__(self, predicate):
        self.predicate = predicate

    def test(self, value):
        return not self.predicate.test(value)


class Predicate(Boolean):
    """ Calls a function to determine truth value. """

    def __init__(self, predicate, *args, **kwargs):
        self.predicate = predicate
        self.args = args
        self.kwargs = kwargs

    def test(self, value):
        try:
            return self.predicate(value, *self.args, **self.kwargs)
        except Exception as ex:
            if log.isEnabledFor(logging.DEBUG):
                log.debug(ex)
            return False


def pred(predicate, *args, **kwargs):
    return partial(Predicate, predicate)


def flip(f):
    """
    Switches position of the first two arguments to f and ensures
    its result is a bool.
    """

    @wraps(f)
    def inner(a, b, *args, **kwargs):
        return bool(f(b, a, *args, **kwargs))

    return inner


class TRUE(Boolean):
    def test(self, value):
        return True


class FALSE(Boolean):
    def test(self, value):
        return False


TRUE = TRUE()
FALSE = FALSE()

lt = pred(operator.lt)
le = pred(operator.le)
eq = pred(operator.eq)
ge = pred(operator.ge)
gt = pred(operator.gt)

isin = pred(flip(operator.contains))

contains = pred(operator.contains)
search = pred(flip(re.search))
matches = search
startswith = pred(str.startswith)
endswith = pred(str.endswith)

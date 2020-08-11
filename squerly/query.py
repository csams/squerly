import re
import yaml
from collections import Counter

from .boolean import Boolean, pred

__all__ = [
    "ANY",
    "Dict",
    "List",
    "Result",
    "Queryable",
    "convert",
    "from_dict",
    "from_yaml",
    "make_child_query",
    "make_model",
    "q",
]

_Dumper = getattr(yaml, "CSafeDumper", yaml.SafeDumper)
_Loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


ANY = None


class _Base(object):
    """
    Base class for primitive Dicts and Lists we'll use to build models.
    """

    def __init__(self, data=None, parent=None):
        if data is not None:
            super(_Base, self).__init__(data)
        else:
            super(_Base, self).__init__()
        self.parent = parent


class Dict(_Base, dict):
    pass


class List(_Base, list):
    pass


class Result(list):
    """
    Contains primitives, Dicts, or Lists.
    """

    def __len__(self):
        return len(list(self.values))

    @property
    def grandchildren(self):
        for v in self:
            if isinstance(v, Dict):
                for i in v.values():
                    yield i
            elif isinstance(v, List):
                for i in v:
                    yield i

    @property
    def values(self):
        for v in self.grandchildren:
            if isinstance(v, List):
                for i in v:
                    yield i
            else:
                yield v


class WhereBoolean(object):
    def __and__(self, other):
        return WhereAnd(self, other)

    def __or__(self, other):
        return WhereOr(self, other)

    def __invert__(self):
        return WhereNot(self)

    def test(self, value):
        raise NotImplementedError()


class WhereAnd(WhereBoolean):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def test(self, value):
        return self.left.test(value) and self.right.test(value)


class WhereOr(WhereBoolean):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def test(self, value):
        return self.left.test(value) or self.right.test(value)


class WhereNot(WhereBoolean):
    def __init__(self, delegate):
        self.delegate = delegate

    def test(self, value):
        return not self.delegate.test(value)


class WherePred(WhereBoolean):
    def __init__(self, pred):
        self.pred = pred

    def test(self, value):
        try:
            return bool(self.pred(value))
        except:
            return False


class WhereQuery(WherePred):
    def __init__(self, name, value=None):
        super(WhereQuery, self).__init__(
            _desugar(name if value is None else (name, value))
        )


make_child_query = WhereQuery
q = WhereQuery


def _desugar(query):
    """
    returns a function that accepts a dict and returns a dict of all name
    value pairs from it that match the query.
    """
    if isinstance(query, tuple):
        name, value = query
        if callable(name):
            name = pred(name)

        if callable(value):
            value = pred(value)

        if isinstance(name, Boolean) and isinstance(value, Boolean):

            def inner(node):
                res = {}
                for k, v in node.items():
                    if name.test(k) and value.test(v):
                        res[k] = v
                return Dict(res, parent=node)

        elif isinstance(name, Boolean):

            def inner(node):
                res = {}
                for k, v in node.items():
                    if name.test(k) and v == value:
                        res[k] = v
                return Dict(res, parent=node)

        elif isinstance(value, Boolean):
            if name is ANY:

                def inner(node):
                    res = {}
                    for k, v in node.items():
                        if value.test(v):
                            res[k] = v
                    return Dict(res, parent=node)

            else:

                def inner(node):
                    try:
                        v = node[name]
                        if value.test(v):
                            return Dict({name: v}, parent=node)
                        return Dict({}, parent=node)
                    except:
                        return Dict({}, parent=node)

        else:

            def inner(node):
                try:
                    v = node[name]
                    if v == value:
                        return Dict({name: v}, parent=node)
                    return Dict({}, parent=node)
                except:
                    return Dict({}, parent=node)

    elif query is ANY:

        def inner(node):
            return node

    elif isinstance(query, Boolean):

        def inner(node):
            res = {}
            for k, v in node.items():
                if query.test(k):
                    res[k] = v
            return Dict(res, parent=node)

    elif callable(query):

        def inner(node):
            res = {}
            for k, v in node.items():
                try:
                    if query(k):
                        res[k] = v
                except:
                    pass
            return Dict(res, parent=node)

    else:

        def inner(node):
            try:
                return Dict({query: node[query]}, parent=node)
            except:
                return Dict({}, parent=node)

    return inner


def _query(pred, value):
    if isinstance(value, Dict):
        res = pred(value)
        return Result([res] if res else [])

    if isinstance(value, List):
        res = Result()
        for v in value:
            r = pred(v)
            if r:
                res.append(r)
        return res

    if isinstance(value, Result):
        res = Result()
        for c in value.grandchildren:
            res.extend(_query(pred, c))
        return res
    return Result()


def _flatten(obj):
    if isinstance(obj, Dict):
        yield obj
        for v in obj.values():
            for i in _flatten(v):
                yield i
    elif isinstance(obj, (List, Result)):
        for v in obj:
            for i in _flatten(v):
                yield i
    else:
        yield obj


class _Queryable:
    __slots__ = ["_value"]

    def __init__(self, value):
        self._value = value

    def keys(self):
        obj = self._value
        if isinstance(obj, Dict):
            return sorted(set(obj.keys()))

        if isinstance(obj, Result):
            obj = obj.grandchildren

        res = set()
        for i in obj:
            try:
                res |= set(i.keys())
            except:
                try:
                    for v in i:
                        res |= set(v.keys())
                except:
                    pass
        return sorted(res)

    get_keys = keys

    @property
    def parents(self):
        value = self._value
        if isinstance(value, Dict):
            return _Queryable(List([value.parent.parent]))

        seen = None
        res = List()
        for v in value:
            p = v.parent
            while isinstance(p, list):
                p = p.parent
            if p is not None and p is not seen:
                res.append(p)
                seen = p
        return _Queryable(res)

    @property
    def roots(self):
        value = self._value if isinstance(self._value, list) else [self._value]
        res = List()
        seen = None
        for v in value:
            if isinstance(v, Dict):
                p = v
                while p.parent is not None:
                    p = p.parent
                if p is not seen:
                    res.append(p)
                    seen = p
        return _Queryable(res)

    @property
    def unique_values(self):
        return sorted(set(self._value.values))

    @property
    def values(self):
        return list(self._value.values)

    @property
    def value(self):
        v = self.values
        assert len(v) == 1
        return v[0]

    def query(self, pred):
        pred = _desugar(pred)
        return _Queryable(_query(pred, self._value))

    def upto(self, pred):
        pred = _desugar(pred)
        value = self._value

        if not isinstance(value, list):
            value = [value]

        seen = None
        res = List()
        for v in value:
            p = v.parent
            while p is not None and p is not seen:
                gp = p.parent
                if isinstance(gp, list):
                    gp = gp.parent
                if gp is seen and seen is not None:
                    res.append(p)
                    break
                if gp is not None:
                    r = _query(pred, gp)
                    if r:
                        res.append(p)
                        seen = gp
                        break
                p = p.parent
        return _Queryable(res)

    def find(self, first, *rest):
        first = _desugar(first)
        queries = [_desugar(arg) for arg in rest]

        def match(node):
            if not isinstance(node, (Dict, List, Result)):
                return Result()

            res = _query(first, node)
            for q in queries:
                if res:
                    res = _query(q, res)
                else:
                    break
            return res

        res = Result()
        for node in _flatten(self._value):
            res.extend(match(node))
        return _Queryable(res)

    def where(self, name, value=None):
        obj = self._value
        if isinstance(obj, Dict):
            obj = obj.values()
        elif isinstance(obj, Result):
            obj = obj.grandchildren

        res = List()

        if isinstance(name, WhereBoolean):
            qry = name
        elif isinstance(name, Boolean):
            qry = WhereQuery(name, value)
        elif callable(name):

            def inner(value):
                if name(_Queryable(value)):
                    return value

            for i in obj:
                res.extend(_query(inner, i))
            return _Queryable(res)
        else:
            qry = WhereQuery(name, value)

        def inner(value):
            if qry.test(value):
                return value

        for i in obj:
            res.extend(_query(inner, i))
        return _Queryable(res)

    def to_df(self):
        import pandas

        return pandas.DataFrame(self.values)

    def most_common(self, n=None):
        return Counter(self.values).most_common(n)

    def __iter__(self):
        for i in self._value:
            yield _Queryable(i)

    def __len__(self):
        return len(self._value)

    def __nonzero__(self):
        return bool(self._value)

    __bool__ = __nonzero__

    def __dir__(self):
        return self.keys() + dir(object)

    def __getattr__(self, name):
        return self.__getitem__(name)

    def __getitem__(self, pred):
        if isinstance(pred, slice):
            return _Queryable(Result(self._value[pred]))
        if isinstance(pred, int):
            return _Queryable(Result([self._value[pred]]))
        return self.query(pred)

    def __lt__(self, other):
        try:
            return self.value < other.value
        except:
            return False

    def __le__(self, other):
        try:
            return self.value <= other.value
        except:
            return False

    def __eq__(self, other):
        try:
            return self.value == other.value
        except:
            return False

    def __ne__(self, other):
        try:
            return self.value != other.value
        except:
            return False

    def __ge__(self, other):
        try:
            return self.value >= other.value
        except:
            return False

    def __gt__(self, other):
        try:
            return self.value > other.value
        except:
            return False

    def matches(self, pattern, flags=0):
        try:
            return re.search(pattern, self.value, flags)
        except:
            return False

    def isin(self, values):
        try:
            return self.value in values
        except:
            return False

    def contains(self, value):
        try:
            return value in self.value
        except:
            return False

    def startswith(self, value):
        try:
            return self.value.startswith(value)
        except:
            return False

    def endswith(self, value):
        try:
            return self.value.endswith(value)
        except:
            return False

    def __repr__(self):
        return yaml.dump(self._value, Dumper=_Dumper)


def make_model(d, parent=None):
    if isinstance(d, list):
        node = List(parent=parent)
        node.extend(make_model(v, parent=node) for v in d)
        return node
    elif isinstance(d, dict):
        node = Dict(parent=parent)
        for k, v in d.items():
            node[k] = make_model(v, parent=node)
        return node
    else:
        return d


convert = make_model
from_dict = make_model


def Queryable(data):
    if not isinstance(data, (List, Dict, Result)):
        data = make_model(data)
    return _Queryable(data)


def from_yaml(path):
    with open(path) as f:
        return Queryable(yaml.load(f, Loader=_Loader))


def Dict_representer(dumper, data):
    # https://yaml.org/type/map.html
    return dumper.represent_mapping("tag:yaml.org,2002:map", data)


yaml.add_representer(Dict, Dict_representer, Dumper=yaml.Dumper)
yaml.add_representer(Dict, Dict_representer, Dumper=_Dumper)
if _Dumper is not yaml.SafeDumper:
    yaml.add_representer(Dict, Dict_representer, Dumper=yaml.SafeDumper)


def List_representer(dumper, data):
    # https://yaml.org/type/seq.html
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data)


yaml.add_representer(List, List_representer, Dumper=yaml.Dumper)
yaml.add_representer(List, List_representer, Dumper=_Dumper)
if _Dumper is not yaml.SafeDumper:
    yaml.add_representer(List, List_representer, Dumper=yaml.SafeDumper)


yaml.add_representer(Result, List_representer, Dumper=yaml.Dumper)
yaml.add_representer(Result, List_representer, Dumper=_Dumper)
if _Dumper is not yaml.SafeDumper:
    yaml.add_representer(Result, List_representer, Dumper=yaml.SafeDumper)

import operator
import re
import uuid
import yaml
from collections import Counter

from .boolean import Boolean, eq, pred, TRUE

__all__ = [
    "ANY",
    "CollectionBase",
    "convert",
    "Dict",
    "List",
    "Queryable",
    "q",
    "WhereQuery",
]

_Dumper = getattr(yaml, "CSafeDumper", yaml.SafeDumper)

ANY = object()


class CollectionBase:
    def __init__(self, data=None, parents=None, source=None):
        super().__init__(data or [])
        self.parents = parents or []
        self.source = source
        self.uid = uuid.uuid4()

    # hash and eq are defined so we can deduplicate as we chase down data
    # structure roots.
    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other):
        try:
            return self.uid == other.uid
        except:
            return False

    def __repr__(self):
        name = self.__class__.__name__
        return f"{name}({super().__repr__()})"


class List(CollectionBase, list):
    """ A list that remembers the data structure to which it belongs. """

    pass


def List_representer(dumper, data):
    # https://yaml.org/type/seq.html
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data)


yaml.add_representer(List, List_representer, Dumper=yaml.Dumper)
yaml.add_representer(List, List_representer, Dumper=_Dumper)
if _Dumper is not yaml.SafeDumper:
    yaml.add_representer(List, List_representer, Dumper=yaml.SafeDumper)


class Dict(CollectionBase, dict):
    """ A dict that remembers the data structure to which it belongs. """

    pass


def Dict_representer(dumper, data):
    # https://yaml.org/type/map.html
    return dumper.represent_mapping("tag:yaml.org,2002:map", data)


yaml.add_representer(Dict, Dict_representer, Dumper=yaml.Dumper)
yaml.add_representer(Dict, Dict_representer, Dumper=_Dumper)
if _Dumper is not yaml.SafeDumper:
    yaml.add_representer(Dict, Dict_representer, Dumper=yaml.SafeDumper)


def _desugar_part(x):
    if isinstance(x, Boolean):
        return x
    if callable(x):
        return pred(x)
    return eq(x)


def get_roots(data):
    results = List()
    seen = set()

    def inner(d):
        if not d.parents and d not in seen:
            results.append(d)
            seen.add(d)
        else:
            for p in d.parents:
                if p not in seen:
                    inner(p)
                seen.add(p)

    if data.parents:
        inner(data)
    return results


class _Queryable:
    __slots__ = ["value"]

    def __init__(self, value):
        self.value = value

    def keys(self):
        keys = []
        seen = set()

        def inner(val):
            if isinstance(val, Dict):
                new = val.keys() - seen
                keys.extend(new)
                seen.update(new)

            if isinstance(val, List):
                for i in val:
                    try:
                        new = i.keys() - seen
                        keys.extend(new)
                        seen.update(new)
                    except:
                        inner(i)

        inner(self.value)
        return sorted(set(keys))

    def most_common(self, top=None):
        return Counter(self.value).most_common(top)

    def unique(self):
        return sorted(set(self.value))

    def sum(self):
        return sum(v for v in self.value if v is not None)

    def to_dataframe(self):
        import pandas

        return pandas.DataFrame(self.value)

    def startswith(self, val):
        try:
            return self.value[0].startswith(val)
        except:
            return False

    def endswith(self, val):
        try:
            return self.value[0].endswith(val)
        except:
            return False

    def matches(self, val, flags=None):
        try:
            return re.search(val, self.value[0], flags=flags)
        except:
            return False

    def __eq__(self, other):
        if not isinstance(other, CollectionBase):
            l = List()
            l.append(other)
            other = Queryable(l)

        if not (self and other):
            return False

        if len(self) != len(other):
            return False

        for i in range(len(self)):
            if self.value[i] != other.value[i]:
                return False
        return True

    def __ne__(self, other):
        if not (self and other):
            return False
        return not self == other

    def _compare(self, op, other):
        """
        Manual comparison since we've overloaded __eq__ on CollectionBase.
        """
        if not isinstance(other, CollectionBase):
            l = List()
            l.append(other)
            other = Queryable(l)

        if not (self and other):
            return False

        try:
            for i in range(len(self.value)):
                if op(self.value[i], other.value[i]):
                    continue
                else:
                    return False
            return True
        except:
            return False

    def __gt__(self, other):
        return self._compare(operator.gt, other)

    def __ge__(self, other):
        return self._compare(operator.ge, other)

    def __lt__(self, other):
        return self._compare(operator.lt, other)

    def __le__(self, other):
        return self._compare(operator.le, other)

    def __add__(self, other):
        value = List()
        for i in (self, other):
            i = Queryable(i)
            if isinstance(i.value, List):
                value.extend(i.value)
            else:
                value.append(i.value)
        return _Queryable(value)

    def _iadd(self, other):
        if not isinstance(self.value, List):
            self.value = List(self.value)

        other = Queryable(other)
        if isinstance(other, List):
            self.value.extend(other.value)
        else:
            self.value.append(other.value)

    @property
    def parents(self):
        gp = []
        seen = set()
        for p in self.value.parents:
            for g in p.parents:
                if g not in seen:
                    gp.append(g)
                    seen.add(g)
        return _Queryable(List(self.value.parents, parents=gp))

    @property
    def roots(self):
        return _Queryable(get_roots(self.value))

    @property
    def sources(self):
        roots = get_roots(self.value)
        sources = [r.source for r in roots if r.source]
        if sources:
            return sources

        return [v.source for v in self.value if v.source]

    def upto(self, query):
        results = List()
        seen = set()

        def inner(val):
            for parent in val.parents:
                if isinstance(parent.value, Dict):
                    r = parent[query]
                else:
                    r = parent.parents[query]

                if r:
                    if isinstance(val.value, Dict):
                        results.append(val.value)
                    else:
                        results.extend(val.value)

                    for p in r.value.parents:
                        if p not in seen:
                            results.parents.append(p)
                            seen.add(p)
                else:
                    inner(parent)

        inner(self)
        return _Queryable(results)

    def find(self, *args):
        results = List()
        queries = [self._desugar(a) for a in args]
        seen = set()

        def run_queries(node):
            n = node
            for q in queries:
                if n.value:
                    n = n._handle_child_query(q)
                else:
                    break

            if n.value:
                results.extend(n.value)
                for p in n.value.parents:
                    if p not in seen:
                        results.parents.append(p)
                        seen.add(p)

            if isinstance(node.value, Dict):
                for i in node.value.values():
                    if isinstance(i, CollectionBase):
                        run_queries(_Queryable(i))
            elif isinstance(node.value, List):
                for i in node.value:
                    if isinstance(i, List):
                        run_queries(_Queryable(i))
                    # we've already picked out values from the dicts above, so
                    # we recurse on their values instead of the individual
                    # dicts directly. Otherwise, we'd double collect those that
                    # hit - once as members of the original list and once
                    # individually.
                    elif isinstance(i, Dict):
                        for v in i.values():
                            run_queries(_Queryable(v))

        run_queries(self)
        return _Queryable(results)

    def __getattr__(self, key):
        # allow dot traversal for simple key names.
        return self.__getitem__(key)

    def __dir__(self):
        # jedi in doesn't tab complete when __getattr__ is defined b/c it could
        # execute arbitrary code. So.. throw caution to the wind.

        # import IPython
        # from traitlets.config.loader import Config

        # IPython.core.completer.Completer.use_jedi = False
        # c = Config()
        # IPython.start_ipython([], user_ns=locals(), config=c)
        return self.keys()

    def __len__(self):
        return len(self.value)

    def __bool__(self):
        return bool(self.value)

    def __iter__(self):
        for i in self.value:
            yield _Queryable(i)

    def _handle_child_query(self, query):
        def inner(val):
            if isinstance(val, Dict):
                r = query(val)
                if r:
                    return List(r, parents=[val])
                return List()
            elif isinstance(val, List):
                results = List()
                for i in val:
                    r = inner(i) if isinstance(i, List) else query(i)
                    if r:
                        results.parents.append(i)
                        results.extend(r)
                return results
            return List()

        return _Queryable(inner(self.value))

    def _desugar_tuple_query(self, key):
        value = self.value
        name_part, value_part = key
        value_query = _desugar_part(value_part) if value is not ANY else TRUE

        if name_part is ANY:

            def query(val):
                results = []
                try:
                    for v in val.values():
                        if isinstance(v, list):
                            for i in v:
                                if value_query.test(i):
                                    results.append(i)
                        else:
                            if value_query.test(v):
                                results.append(v)
                except:
                    return []
                return results

        elif not callable(name_part):

            def query(val):
                try:
                    v = val[name_part]
                    if value_query.test(v):
                        if isinstance(v, list):
                            results = []
                            for i in v:
                                if value_query.test(i):
                                    results.append(i)
                            return results
                        else:
                            return [v] if value_query.test(v) else []
                except:
                    return []

        else:
            name_query = _desugar_part(name_part)

            def query(val):
                results = []
                try:
                    for k, v in val.items():
                        if name_query.test(k):
                            if isinstance(v, list):
                                for i in v:
                                    if value_query.test(i):
                                        results.append(i)
                            else:
                                if value_query.test(v):
                                    results.append(v)
                except:
                    return []
                return results

        return query

    def _desugar_name_query(self, key):
        if key is ANY:

            def query(val):
                results = []
                try:
                    for v in val.values():
                        if isinstance(v, list):
                            results.extend(v)
                        else:
                            results.append(v)
                except:
                    return []
                return results

        elif not callable(key):

            def query(val):
                try:
                    r = val[key]
                    return r if isinstance(r, list) else [r]
                except:
                    return []

        else:
            name_query = _desugar_part(key)

            def query(val):
                results = []
                try:
                    for k, v in val.items():
                        if name_query.test(k):
                            if isinstance(v, list):
                                results.extend(v)
                            else:
                                results.append(v)
                except:
                    return []
                return results

        return query

    def _desugar(self, key):
        if isinstance(key, tuple):
            return self._desugar_tuple_query(key)
        return self._desugar_name_query(key)

    def __getitem__(self, key):
        if isinstance(key, int):
            return Queryable(self.value[key])

        if isinstance(key, slice):
            vals = List(self.value[key])
            seen = set()
            for v in vals:
                for p in v.parents:
                    if p not in seen:
                        vals.parents.append(p)
                        seen.add(p)
            return Queryable(vals)

        query = self._desugar(key)
        return self._handle_child_query(query)

    def _handle_where_query(self, query):
        seen = set()

        def inner(val):
            results = List()
            for i in val:
                if isinstance(i, List):
                    r = inner(i)
                    if r:
                        results.append(i)
                        for p in i.parents:
                            if p not in seen:
                                results.parents.append(p)
                                seen.add(p)
                elif query(i):
                    results.append(i)
                    for p in i.parents:
                        if p not in seen:
                            results.parents.append(p)
                            seen.add(p)
            return results

        return _Queryable(inner(self.value))

    def _desugar_where(self, query, value):
        # if value is defined, the caller didn't bother to make a WhereQuery
        if value is not ANY:
            query = WhereQuery(query, value)

            def runquery(val):
                return query.test(val)

        # query already contains WhereQuery instances. We check for Boolean
        # because query might some combination of WhereQuerys.
        elif isinstance(query, Boolean):

            def runquery(val):
                return query.test(val)

        # value is not defined, and query is not a WhereQuery. If query is a
        # callable, it's just a regular function or lambda. We assume the
        # caller wants to manually inspect each item.
        elif callable(query):

            def runquery(val):
                try:
                    return query(_Queryable(val))
                except:
                    return False

        # this handles the case where the caller wants to simply check for the
        # existence of a key without needing to construct a WhereQuery. Because
        # of the above checks, query here can be only a primitive value.
        else:
            query = WhereQuery(query)

            def runquery(val):
                return query.test(val)

        return runquery

    def where(self, query, value=ANY):
        """
        Accepts WhereQuery instances, combinations of WhereQuery instances, or
        a callable that will be passed a Queryable version of each item. Where
        queries only make sense against lists.
        """

        runquery = self._desugar_where(query, value)
        return self._handle_where_query(runquery)

    def __repr__(self):
        return yaml.dump(self.value, Dumper=_Dumper)


class WhereQuery(Boolean):
    """
    Used to combine predicates for multiple keys in a dictionary.

    conf.find("conditions").where(q("status", "True") & q("message", matches("error|fail")))
    Only use in where queries.
    """

    def __init__(self, name_part, value_part=ANY):
        value_query = _desugar_part(value_part) if value_part is not ANY else TRUE

        if name_part is ANY:
            self.query = lambda val: any(value_query.test(v) for v in val.values())
        elif not callable(name_part):
            self.query = (
                lambda val: value_query.test(val[name_part])
                if name_part in val
                else False
            )
        else:
            name_query = _desugar_part(name_part)
            self.query = lambda val: any(
                name_query.test(k) and value_query.test(v) for k, v in val.items()
            )

    def test(self, value):
        try:
            return self.query(value)
        except:
            return False


q = WhereQuery


def convert(data, parent=None):
    """
    Convert nest of dicts and lists into Dicts and Lists that contain
    pointers to their parents.
    """
    if isinstance(data, dict):
        d = Dict(parents=[parent] if parent is not None else [])
        d.update({k: convert(v, parent=d) for k, v in data.items()})
        return d

    if isinstance(data, list):
        l = List(parents=[parent] if parent is not None else [])
        l.extend(convert(i, parent=l) for i in data)
        return l

    return data


def Queryable(data=None):
    """ Use this function to make your data queryable. """
    if data is None:
        return _Queryable(List())

    if isinstance(data, _Queryable):
        return data

    if isinstance(data, CollectionBase):
        return _Queryable(data)

    return _Queryable(convert(data))

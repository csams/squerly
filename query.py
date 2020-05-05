import uuid
from pprint import pformat

from boolean import Boolean, eq, pred, TRUE

__all__ = [
    "CollectionBase",
    "Dict",
    "List",
    "NONE",
    "Queryable",
    "WhereQuery",
    "q"
]

NONE = object()


def _desugar(x):
    if isinstance(x, Boolean):
        return x
    if callable(x):
        return pred(x)
    return eq(x)


class CollectionBase:
    def __init__(self, data=None, parents=None):
        super().__init__(data or [])
        self.parents = parents or []
        self.uid = uuid.uuid4()

    # hash and eq are defined so we can deduplicate as we chase down data
    # structure roots.
    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other):
        return self.uid == other.uid


class List(CollectionBase, list):
    """ A list that remembers the data structure to which it belongs. """
    pass


class Dict(CollectionBase, dict):
    """ A dict that remembers the data structure to which it belongs. """
    pass


class _Queryable:
    __slots__ = ["value"]

    def __init__(self, value):
        self.value = value

    def get_keys(self):
        if isinstance(self.value, Dict):
            return sorted(self.value)

        if isinstance(self.value, List):
            keys = []
            for i in self.value:
                try:
                    keys.extend(i.keys())
                except:
                    pass
            return sorted(set(keys))

    @property
    def unique_values(self):
        return sorted(set(self.value))

    @property
    def values(self):
        return sorted(self.value)

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

    def __getattr__(self, key):
        # allow dot access traversal for simple key names.
        return self.__getitem__(key)

    def __dir__(self):
        # jedi in ipython doesn't tab complete when __getattr__ is defined
        # b/c it could execute arbitrary code. To get around it, disable
        # jedi.

        # import IPython
        # from traitlets.config.loader import Config

        # IPython.core.completer.Completer.use_jedi = False
        # c = Config()
        # IPython.start_ipython([], user_ns=locals(), config=c)
        return self.get_keys()

    def __len__(self):
        return len(self.value)

    def __bool__(self):
        return bool(self.value)

    def _handle(self, query):

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

    def _handle_tuple(self, key):
        value = self.value
        name_part, value_part = key
        value_query = _desugar(value_part) if value is not NONE else TRUE

        if name_part is NONE:
            def query(val):
                return [v for v in val.values() if value_query.test(v)]
        elif not callable(name_part):
            def query(val):
                try:
                    v = val[name_part]
                    return [v] if value_query.test(v) else []
                except:
                    return []
        else:
            name_query = _desugar(name_part)

            def query(val):
                results = [v for k, v in val.items() if name_query.test(k) and value_query.test(v)]
                return results

        return self._handle(query)

    def _handle_name_query(self, key):
        if key is NONE:
            def query(val):
                return list(val.values())
        elif not callable(key):
            def query(val):
                try:
                    return [val[key]]
                except:
                    return []
        else:
            name_query = _desugar(key)

            def query(val):
                return [v for k, v in val.items() if name_query.test(k)]

        return self._handle(query)

    def __getitem__(self, key):
        # support for data[(name_query, value_query)]
        if isinstance(key, tuple):
            return self._handle_tuple(key)

        # support for data[name_query]
        return self._handle_name_query(key)

    def _handle_where_callable(self, func):
        # In this function, func is passed a _Queryable instance instead of raw
        # values like in handle_where_query. This enables where queries that
        # look deep into the structure of each item.
        def inner(val):
            if isinstance(val, Dict):
                if func(self):
                    return List([val], parents=val.parents)
                return List()

            if isinstance(val, List):
                results = List()
                for i in val:
                    if isinstance(i, List):
                        # handle nested lists
                        r = inner(i)
                        if r:
                            results.extend(r)
                    elif func(_Queryable(i)):
                        results.append(i)
                if results:
                    results.parents.append(val)
                return results

            return List()
        return _Queryable(inner(self.value))

    def _handle_where_query(self, query):
        def inner(val):
            if isinstance(val, Dict):
                if query.test(val):
                    return List([val], parents=val.parents)
                return List()

            if isinstance(val, List):
                results = List()
                for i in val:
                    if isinstance(i, List):
                        # handle nested lists
                        r = inner(i)
                        if r:
                            results.extend(r)
                    elif query.test(i):
                        results.append(i)
                if results:
                    results.parents.append(val)
                return results

            return List()
        return _Queryable(inner(self.value))

    def where(self, query, value=NONE):
        """
        Accepts WhereQuery instances, combinations of WhereQuery instances, or
        a callable that will be passed a Queryable version of each item.
        """

        # if value is defined, the caller didn't bother to make a WhereQuery
        if value is not NONE:
            return self._handle_where_query(WhereQuery(query, value))

        # query already contains WhereQuery instances. We check for Boolean
        # because query might some combination of WhereQuerys.
        if isinstance(query, Boolean):
            return self._handle_where_query(query)

        # value is not defined, and query is not a WhereQuery. If query is a
        # callable, it's just a regular function or lambda. We assume the
        # caller wants to manually inspect each item.
        if callable(query):
            return self._handle_where_callable(query)

        # this handles the case where the caller wants to simply check for the
        # existence of a key without needing to construct a WhereQuery. Because
        # of the above checks, query here can be only a primitive value.
        return self._handle_where_query(WhereQuery(query))

    def __repr__(self):
        return f"_Queryable({pformat(self.value)})"


class WhereQuery(Boolean):
    """ Only use in where queries. """
    def __init__(self, name_part, value_part=NONE):
        value_query = _desugar(value_part) if value_part is not NONE else TRUE

        if name_part is NONE:
            self.query = lambda val: any(value_query.test(v) for v in val.values())
        elif not callable(name_part):
            self.query = lambda val: value_query.test(val[name_part]) if name_part in val else False
        else:
            name_query = _desugar(name_part)
            self.query = lambda val: any(name_query.test(k) and value_query.test(v) for k, v in val.items())

    def test(self, value):
        try:
            return self.query(value)
        except:
            return False


q = WhereQuery


def _convert(data, parent=None):
    """
    Convert nest of dicts and lists into Dicts and Lists that contain
    pointers to their parents.
    """
    if isinstance(data, dict):
        d = Dict(parents=[parent] if parent is not None else [])
        d.update({k: _convert(v, parent=d) for k, v in data.items()})
        return d

    if isinstance(data, list):
        l = List(parents=[parent] if parent is not None else [])
        l.extend(_convert(i, parent=l) for i in data)
        return l

    return data


def Queryable(data):
    if isinstance(data, _Queryable):
        return data

    if isinstance(data, CollectionBase):
        return _Queryable(data)

    return _Queryable(_convert(data))

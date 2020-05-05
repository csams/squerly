import uuid
from pprint import pformat

from boolean import Boolean, eq, pred, TRUE

__all__ = [
    "CollectionBase",
    "Dict",
    "DictQuery",
    "List",
    "Queryable",
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

    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other):
        return self.uid == other.uid


class List(CollectionBase, list):
    pass


class Dict(CollectionBase, dict):
    pass


class _Queryable:
    __slots__ = ["value"]

    def __init__(self, value):
        self.value = value

    def get_keys(self):
        if isinstance(self.value, dict):
            return sorted(self.value)

        if isinstance(self.value, list):
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
        return self.__getitem__(key)

    def __dir__(self):
        return self.get_keys()

    def __len__(self):
        return len(self.value)

    def __bool__(self):
        return bool(self.value)

    def _handle_callable(self, func):
        value = self.value
        if isinstance(value, Dict):
            return self if func(self) else _Queryable(Dict())

        if isinstance(value, List):
            results = List()
            for i in value:
                if func(_Queryable(i)):
                    results.parents.extend(i.parents)
                    results.append(i)
            return results

        return _Queryable(List())

    def _handle_dict_query(self, key):
        value = self.value
        if isinstance(value, Dict):
            return self if key.test(value) else _Queryable(Dict())

        if isinstance(value, List):
            results = List()
            for i in value:
                if key.test(i):
                    results.parents.extend(i.parents)
                    results.append(i)
            return _Queryable(results)

        return _Queryable(List())

    def _handle(self, query):
        value = self.value

        def inner(val):
            if isinstance(val, Dict):
                r = query(val)
                if r:
                    return List(r, parents=[val])
                return List()

            elif isinstance(val, List):
                results = List()
                for i in val:
                    if isinstance(i, List):
                        return inner(i)
                    else:
                        r = query(i)
                        if r:
                            results.parents.append(i)
                            results.extend(r)
                return results
            return List()
        return _Queryable(inner(value))

    def _handle_tuple(self, key):
        value = self.value
        name_part, value_part = key
        value_query = _desugar(value_part) if value is not None else TRUE

        if name_part is None:
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
        if key is None:
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
        if isinstance(key, tuple):
            return self._handle_tuple(key)

        return self._handle_name_query(key)

    def where(self, query, value=NONE):
        """
        Accepts DictQuery instances, combinations of DictQuery instances, or
        a callable that will be passed a Queryable version of each item.
        """
        if value is not NONE:
            return self._handle_dict_query(DictQuery(query, value))

        if isinstance(query, Boolean):
            return self._handle_dict_query(query)

        if callable(query):
            return self._handle_callable(query)

    def __repr__(self):
        return f"_Queryable({pformat(self.value)})"


class DictQuery(Boolean):
    """ Only use in where queries. """
    def __init__(self, name_part, value_part=None):
        self.name_part = name_part
        self.value_query = _desugar(value_part) if value_part is not None else TRUE

    def test(self, value):
        try:
            if self.name_part is None:
                return any(self.value_query.test(v) for v in value.values())

            if not callable(self.name_part):
                if self.name_part not in value:
                    return False
                return self.value_query.test(value[self.name_part])

            self.name_query = _desugar(self.name_part)
            return any(self.name_query.test(k) and self.value_query.test(v) for k, v in value.items())
        except:
            return False


q = DictQuery


def _convert(data, parent=None):

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

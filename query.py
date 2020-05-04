from pprint import pformat
from boolean import Boolean, eq, pred, TRUE


def desugar(x):
    if isinstance(x, Boolean):
        return x
    if callable(x):
        return pred(x)
    return eq(x)


class Queryable:
    __slots__ = ["value", "parent"]

    def __init__(self, value, parent=None):
        self.value = value
        self.parent = parent

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

    def __getattr__(self, key):
        return self.__getitem__(key)

    def __dir__(self):
        return self.get_keys()

    def __len__(self):
        return len(self.value)

    def __bool__(self):
        return bool(self.value)

    def _handle_callable(self, query, value):
        if isinstance(value, dict):
            return Queryable([value], parent=self) if query(Queryable([value])) else Queryable([], parent=self)

        if isinstance(value, list):
            return Queryable([i for i in value if query(Queryable([i]))], parent=self)

        return Queryable([], parent=self)

    def _handle_dict_query(self, key, value):
        if isinstance(value, dict):
            return Queryable([value], parent=self) if key.test(value) else Queryable([], parent=self)

        if isinstance(value, list):
            return Queryable([i for i in value if key.test(i)], parent=self)

        return Queryable([], parent=self)

    def _handle_tuple(self, key, value):
        name_part, value_part = key
        value_query = desugar(value_part) if value is not None else TRUE

        if name_part is None:
            def helper(val):
                return [v for v in val.values() if value_query.test(v)]
        elif not callable(name_part):
            def helper(val):
                try:
                    v = val[name_part]
                    return [v] if value_query.test(v) else []
                except:
                    return []
        else:
            name_query = desugar(name_part)

            def helper(val):
                results = [v for k, v in val.items() if name_query.test(k) and value_query.test(v)]
                return results

        if isinstance(value, dict):
            return Queryable(helper(value), parent=self)

        elif isinstance(value, list):
            results = []
            for i in value:
                results.extend(helper(i))
            return Queryable(results, parent=self)

    def _handle_name_query(self, key, value):
        if key is None:
            def helper(val):
                return list(val.values())
        elif not callable(key):
            def helper(val):
                try:
                    return [val[key]]
                except:
                    return []
        else:
            name_query = desugar(key)

            def helper(val):
                return [v for k, v in val.items() if name_query.test(k)]

        if isinstance(value, dict):
            return Queryable(helper(value), parent=self)

        if isinstance(value, list):
            results = []
            for i in value:
                results.extend(helper(i))
            return Queryable(results, parent=self)

        return Queryable([], parent=self)

    def __getitem__(self, key):
        if isinstance(key, tuple):
            return self._handle_tuple(key, self.value)

        if isinstance(key, slice):
            return Queryable(self.value[key], parent=self)

        return self._handle_name_query(key, self.value)

    def where(self, query):
        """ Should be passed only DictQuery instances or boolean combinations of them. """
        if isinstance(query, Boolean):
            return self._handle_dict_query(query, self.value)

        if callable(query):
            return self._handle_callable(query, self.value)

    def __repr__(self):
        return f"Queryable({pformat(self.value)})"


class DictQuery(Boolean):
    """ Only for use in where queries. """
    def __init__(self, name_part, value_part=None):
        self.name_part = name_part
        self.value_query = desugar(value_part) if value_part is not None else TRUE

    def test(self, value):
        if self.name_part is None:
            return any(self.value_query.test(v) for v in value.values())

        if not callable(self.name_part):
            if self.name_part not in value:
                return False
            return self.value_query.test(value[self.name_part])

        self.name_query = desugar(self.name_part)
        return any(self.name_query.test(k) and self.value_query.test(v) for k, v in value.items())


q = DictQuery

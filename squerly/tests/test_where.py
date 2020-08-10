from squerly.query import Queryable, q


DICT_DATA = Queryable(
    {
        "a": 1,
        "b": 2,
        "c": [
            {"foo": "foo value 0", "bar": "bar value 0"},
            {"foo": "foo value 1", "bar": "bar value 1", "baz": {"foo": "foo value 2"}},
        ],
    }
)

LIST_DATA = Queryable(
    [
        {"foo": "foo value 0", "bar": "bar value 0"},
        {"foo": "foo value 1", "bar": "bar value 1", "baz": {"foo": "foo value 2"}},
    ]
)


def test_where_simple_name():
    assert len(DICT_DATA.c.where("foo")) == 2
    assert len(LIST_DATA.where("foo")) == 2


def test_where_simple_name_value():
    assert len(DICT_DATA.c.where("foo", "foo value 0")) == 1
    assert len(LIST_DATA.where("foo", "foo value 0")) == 1


def test_where_complex_name_value():
    assert len(DICT_DATA.c.where("foo", "foo value 0")) == 1
    assert len(LIST_DATA.where("foo", "foo value 0")) == 1


def test_where_lambda():
    def predicate(s):
        return s.foo.value == "foo value 0"

    res = DICT_DATA.c.where(predicate)
    assert len(res) == 1

    res = LIST_DATA.where(predicate)
    assert len(res) == 1


def test_where_multiple_predicates():
    assert len(DICT_DATA.c.where(q("foo") & q("bar"))) == 2
    assert len(DICT_DATA.c.where(q("foo") & q("bar") & q("baz"))) == 1

    assert len(LIST_DATA.where(q("foo") & q("bar"))) == 2
    assert len(LIST_DATA.where(q("foo") & q("bar") & q("baz"))) == 1

from squerly.boolean import eq, matches
from squerly.query import Queryable


DICT_DATA = Queryable(
    {
        "a": 1,
        "b": 2,
        "c": [
            {"foo": "foo value 0", "bar": "bar value 0"},
            {"foo": "foo value 1", "bar": "bar value 1"},
        ],
    }
)

LIST_DATA = Queryable(
    [
        {"foo": "foo value 0", "bar": "bar value 0"},
        {"foo": "foo value 1", "bar": "bar value 1"},
    ]
)


def test_simple_name_query():
    assert len(DICT_DATA["a"]) == 1
    assert len(DICT_DATA.a) == 1
    assert len(DICT_DATA["c"]) == 2
    assert len(DICT_DATA.c) == 2
    assert len(DICT_DATA["c"]["foo"]) == 2
    assert len(DICT_DATA.c.foo) == 2

    assert len(LIST_DATA["foo"]) == 2
    assert len(LIST_DATA.foo) == 2


def test_simple_value_query():
    assert len(DICT_DATA["a", 1]) == 1
    assert len(DICT_DATA["c"]["foo", "foo value 0"]) == 1

    assert len(LIST_DATA["foo", "foo value 0"]) == 1


def test_complex_name_query():
    assert len(DICT_DATA[matches("a")]) == 1
    assert len(DICT_DATA["c"][matches("foo")]) == 2

    assert len(LIST_DATA[matches("foo")]) == 2


def test_complex_value_query():
    assert len(DICT_DATA["a", eq(1)]) == 1
    assert len(DICT_DATA["c"]["foo", matches("foo value 0")]) == 1

    assert len(LIST_DATA["foo", matches("foo value 0")]) == 1
    assert len(LIST_DATA["foo", matches("foo value.*")]) == 2

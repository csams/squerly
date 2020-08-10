from squerly.boolean import eq, matches
from squerly.query import Queryable


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


def test_simple_find():
    assert len(DICT_DATA.find("a")) == 1
    assert len(DICT_DATA.find("b")) == 1
    assert len(DICT_DATA.find("c")) == 2
    assert len(DICT_DATA.find("foo")) == 3

    assert len(LIST_DATA.find("foo")) == 3


def test_deep_find():
    assert len(DICT_DATA.find("c", "foo")) == 2

    assert len(LIST_DATA.find("baz", "foo")) == 1


def test_complex_find():
    assert len(DICT_DATA.find(("a", eq(1)))) == 1
    assert len(DICT_DATA.find(matches("foo"))) == 3
    assert len(DICT_DATA.find((matches("foo"), matches("foo value.*")))) == 3
    assert len(DICT_DATA.find((matches("foo"), matches("foo value (0|1)")))) == 2

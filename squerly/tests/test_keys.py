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


def test_keys():
    assert len(LIST_DATA.baz.keys()) == 1
    assert len(LIST_DATA.keys()) == 3
    assert len(DICT_DATA.keys()) == 3
    assert len(DICT_DATA.c.keys()) == 3

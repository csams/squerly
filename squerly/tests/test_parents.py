from squerly import Queryable


A = Queryable({
    "a": 1,
    "b": 2,
    "c": {
        "a": 2,
        "b": 4
    }
})

B = Queryable([
    {
        "a": 1,
        "b": 2,
        "c": {
            "a": 2,
            "b": 4
        },
    }
])

C = Queryable([
    {
        "top": {
            "a": 1,
            "b": 2,
            "c": {
                "a": 2,
                "b": 4
            }
        },
    },
    {
        "top": {
            "a": 9,
            "b": 6,
            "c": {
                "a": 8,
                "b": 7
            }
        },
    },
])


def test_parents_nested_children():
    res = C.find("a")
    assert len(res) == 4
    res = C.find("a").parents
    assert len(res) == 4

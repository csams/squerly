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

D = Queryable([
    {
        "top": {
            "a": {
                "r": {
                    "b": 45
                }
            },
            "d": 2,
            "c": {
                "a": 2,
                "b": 4
            }
        },
    }
])


def test_upto_nested_children():
    res = C.find("a").upto("top")
    assert len(res) == 2, res


def test_upto_nested_children_ambiguous_top():
    res = D.find("b").upto("a")
    assert len(res) == 1, res

    res = D.find("b").upto("c")
    assert len(res) == 1, res

"""
Very inefficient lsof parser.

It calculates header boundaries and then parses rows by checking for
intersection with each field's boundaries. Something like this is needed
because lsof doesn't keep values strictly inside the boundaries of their
headers, and fields aren't unambiguously delimited in rows with missing
values.
"""
from subprocess import check_output

from squerly import Queryable


def _get_intervals(line):
    looking_for_start = True
    results = []
    t = 0
    for i, c in enumerate(line):
        if looking_for_start:
            if c.isspace():
                continue
            t = i
            looking_for_start = False
        else:
            if not c.isspace():
                continue
            results.append((t, i))
            looking_for_start = True
    if t and i:
        results.append((t, i + 1))
    return results


def _intersect(a, b):
    return max((a[0], b[0])) < min((a[1], b[1]))


def parse(content):
    top = content[0]
    header_intervals = _get_intervals(top)
    headers = dict((top[l:r].lower(), (l, r)) for (l, r) in header_intervals)
    results = []
    for line in content[1:]:
        one = []
        intervals = _get_intervals(line)
        for i in intervals:
            val = line[slice(*i)]
            for key, h in headers.items():
                if _intersect(i, h):
                    one.append((key, val))
                    break
        results.append(dict(one))
    return results


def load():
    return check_output(["lsof"], encoding="utf-8").splitlines()


def get():
    return Queryable(parse(load()))

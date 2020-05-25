import string
from subprocess import check_output

from squerly import Queryable

cruft = string.whitespace + "\u25cf"


def parse(content):
    results = []
    columns = [c.lower() for c in content[0].split()]
    num_splits = len(columns) - 1
    for line in content[1:]:
        line = line.strip(cruft)
        if not line:
            break
        row = dict(zip(columns, line.split(None, num_splits)))
        results.append(row)
    return results


def load():
    return check_output(
        ["systemctl", "-l", "-a", "list-units"], encoding="utf-8"
    ).splitlines()


def get():
    return Queryable(parse(load()))

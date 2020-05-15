from subprocess import check_output

from squerly import Queryable


def parse(content):
    columns = ["unit_file", "state"]
    results = []
    for line in content[1:]:
        line = line.strip()
        if not line:
            break
        row = dict(zip(columns, line.split(None, 1)))
        results.append(row)
    return results


def load():
    return check_output(["systemctl", "list-unit-files"], encoding="utf-8").splitlines()


def get():
    return Queryable(parse(load()))

import shlex
from subprocess import check_output

from squerly import Queryable


def parse(content):
    header = ["filesystem", "blocks", "used", "available", "capacity", "mount"]

    def fix_types(parts):
        results = []
        for p in parts:
            if p == "-":
                results.append(0.0)
            elif p[0].isdigit():
                results.append(float(p.rstrip("%")))
            else:
                results.append(p)
        return results

    results = []
    num = len(header) - 1
    for line in content[1:]:
        parts = line.strip().split(None, num)
        parts = fix_types(parts)
        data = dict(zip(header, parts))
        data["capacity"] = data["capacity"] / 100
        results.append(data)

    return results


def load():
    return check_output(shlex.split("df -alP"), encoding="utf-8").splitlines()


def get():
    return Queryable(parse(load()))

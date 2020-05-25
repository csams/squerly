import shlex
from subprocess import check_output

from squerly import Queryable


def parse(content):
    results = []
    header = [
        "user",
        "pid",
        "cpu",
        "mem",
        "vsz",
        "rss",
        "tty",
        "stat",
        "start",
        "time",
        "command",
    ]
    hl = len(header) - 1
    for line in content[1:]:
        parts = [l.strip() for l in line.split(None, hl)]
        data = dict(zip(header, parts))
        data["pid"] = int(data["pid"])
        data["cpu"] = float(data["cpu"])
        data["mem"] = float(data["mem"])
        data["vsz"] = float(data["vsz"])
        data["rss"] = float(data["rss"])
        results.append(data)
    return results


def load():
    return check_output(shlex.split("ps aux"), encoding="utf-8").splitlines()


def get():
    return Queryable(parse(load()))

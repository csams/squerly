from squerly import Queryable


def parse(content):
    mem = {}
    for line in content:
        line = line.strip()
        k, v = line.split(":", 1)
        k = k.strip().rstrip(")").replace(" (", "_").lower()
        v = v.strip()
        v = int(v.split()[0]) * 1024 if v.endswith("kB") else int(v)
        mem[k] = v
    return mem


def load():
    for path in ["/proc/meminfo", "/meminfo"]:
        try:
            with open(path) as f:
                return [l.rstrip() for l in f]
        except:
            pass
    raise Exception("Can't load meminfo.")


def get():
    return Queryable(parse(load()))

#!/usr/bin/env python3
import argparse
import logging
import os
import re
import yaml

from queryable import *  # noqa
from queryable import convert, List, Queryable


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument("paths", nargs="+")
    return p.parse_args()


def _get_files(path):
    with os.scandir(path) as it:
        for ent in it:
            if ent.is_dir(follow_symlinks=False):
                for pth in _get_files(ent.path):
                    yield pth
            elif ent.is_file(follow_symlinks=False):
                yield ent.path


def analyze(paths, ignore=".*(log|txt)$"):
    ignore = re.compile(ignore).search if ignore else lambda x: False
    results = List()

    def load(p):
        if not ignore(p):
            try:
                with open(p) as f:
                    doc = yaml.load(f, Loader=yaml.CSafeLoader)
                    if isinstance(doc, (list, dict)):
                        d = convert(doc)
                        d.source = p
                        results.append(d)
            except:
                pass

    for path in paths:
        if os.path.isfile(path):
            load(path)
        elif os.path.isdir(path):
            for p in _get_files(path):
                load(p)

    return Queryable(results)


def main():
    args = parse_args()
    logging.basicConfig(level=(logging.DEBUG if args.verbose else logging.INFO))

    conf = analyze(args.paths)

    import IPython
    from traitlets.config.loader import Config

    IPython.core.completer.Completer.use_jedi = False
    c = Config()
    ns = {}
    ns.update(globals())
    ns.update(locals())
    IPython.start_ipython([], user_ns=ns, config=c)


if __name__ == "__main__":
    main()

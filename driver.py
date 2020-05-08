#!/usr/bin/env python3
import os
import re
import yaml

import queryable  # noqa
from queryable.models import df, lsof, lsof2, meminfo, ps, rpms  # noqa
from queryable import *  # noqa
from queryable import convert, List, Queryable

__all__ = ["df", "lsof", "lsof2", "meminfo", "ps", "rpms", "analyze"] + queryable.__all__


def _get_files(path):
    with os.scandir(path) as it:
        for ent in it:
            if ent.is_dir(follow_symlinks=False):
                for pth in _get_files(ent.path):
                    yield pth
            elif ent.is_file(follow_symlinks=False):
                yield ent.path


def analyze(path, ignore=".*(log|txt)$"):
    ignore = re.compile(ignore).search if ignore else lambda x: False
    results = List()
    for p in _get_files(path):
        if not ignore(p):
            try:
                with open(p) as f:
                    doc = yaml.load(f, Loader=yaml.CSafeLoader)
                    if isinstance(doc, (list, dict)):
                        results.append(convert(doc))
            except:
                pass
    return Queryable(results)

#!/usr/bin/env python3
import boolean
import os
import query
import re
import yaml

from boolean import *  # noqa
from models import df, lsof, meminfo, ps, rpms  # noqa
from query import convert, List, Queryable
from query import *  # noqa

__all__ = ["df", "lsof", "meminfo", "ps", "rpms", "analyze"] + boolean.__all__ + query.__all__


def _get_all_files(path):
    with os.scandir(path) as it:
        for ent in it:
            if ent.is_dir(follow_symlinks=False):
                for pth in _get_all_files(ent.path):
                    yield pth
            elif ent.is_file(follow_symlinks=False):
                yield ent.path


def analyze(path, ignore=".*(log|txt)$"):
    ignore = re.compile(ignore).search
    results = List()
    for p in _get_all_files(path):
        if not ignore(p):
            try:
                with open(p) as f:
                    doc = yaml.load(f, Loader=yaml.CSafeLoader)
                    if isinstance(doc, (list, dict)):
                        results.append(convert(doc))
            except:
                pass
    return Queryable(results)

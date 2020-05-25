#!/usr/bin/env python3

import squerly  # noqa
from squerly.models import df, lsof, lsof2, meminfo, ps, rpms  # noqa
from squerly import *  # noqa

__all__ = ["df", "lsof", "lsof2", "meminfo", "ps", "rpms"] + squerly.__all__

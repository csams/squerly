import json
import shlex
from subprocess import check_output

from squerly import Queryable


def parse(content):
    return [json.loads(l) for l in content]


def load():
    rpm_cmd = 'rpm -qa --qf \'\\{"name":"%{NAME}","epoch":"%{EPOCH}","version":"%{VERSION}","release":"%{RELEASE}","arch":"%{ARCH}","installtime":"%{INSTALLTIME:date}","buildtime":"%{BUILDTIME}","vendor":"%{VENDOR}","buildhost":"%{BUILDHOST}","sigpgp":"%{SIGPGP:pgpsig}"\\}\n\''
    return check_output(shlex.split(rpm_cmd), encoding="utf-8").splitlines()


def get():
    return Queryable(parse(load()))

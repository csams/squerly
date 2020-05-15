import logging
from subprocess import check_output

from squerly import Dict, List, Queryable

log = logging.getLogger(__name__)

_table = {
    "a": ("access_mode", str),
    "c": ("command", str),
    "C": ("structure_share_count", int),
    "d": ("device_character_code", str),
    "D": ("device_number", str),
    "f": ("descriptor", str),
    "F": ("structure_address", str),
    "G": ("flags", str),
    "g": ("gid", int),
    "i": ("inode_number", int),
    "K": ("task_id", int),
    "k": ("link_count", int),
    "l": ("lock_status", str),
    "L": ("login_name", str),
    "m": ("repeated_output_marker", str),
    "M": ("task_command", str),
    "n": ("file_name", str),
    "N": ("node_identifier", str),
    "o": ("offset", str),
    "p": ("pid", int),
    "P": ("protocol_name", str),
    "r": ("raw_device_number", str),
    "R": ("ppid", int),
    "s": ("size", int),
    "S": ("stream", str),
    "t": ("type", str),
    "TQR": ("tcp_read_queue_size", int),
    "TQS": ("tcp_send_queue_size", int),
    "TSO": ("tcp_socket_options", str),
    "TSS": ("tcp_socket_states", str),
    "TST": ("tcp_connection_state", str),
    "TTF": ("tcp_flags", str),
    "TWR": ("tcp_window_read_size", int),
    "TWS": ("tcp_window_write_size", int),
    "u": ("uid", int),
    "z": ("zone_name", str),
    "Z": ("selinux_security_context", str),
    "0": ("use_nul_sep", str),
    "1": ("dialect_specific_1", str),
    "2": ("dialect_specific_2", str),
    "3": ("dialect_specific_3", str),
    "4": ("dialect_specific_4", str),
    "5": ("dialect_specific_5", str),
    "6": ("dialect_specific_6", str),
    "7": ("dialect_specific_7", str),
    "8": ("dialect_specific_8", str),
    "9": ("dialect_specific_9", str),
}


def parse(content):
    results = List()
    one = Dict(parents=[results])
    net = False
    for line in content:
        line = line.rstrip()

        if line[0] == "T":
            k, v = line.split("=", 1)
            net = True
        else:
            k, v = line[0], line[1:]

        try:
            key, _type = _table[k]
            # start a new record
            if key in one:
                # overloaded prefix
                if net and "file_name" in one:
                    one["internet_address"] = one["file_name"]
                    del one["file_name"]
                results.append(one)
                one = Dict(parents=[results])
                net = False

            one[key] = _type(v) if v != "" else None
        except KeyError:
            log.warn(f"Skipping unknown key: %s", k)
    if one:
        results.append(one)

    return results


def load():
    return check_output(["lsof", "-F"], encoding="utf-8").splitlines()


def get():
    return Queryable(parse(load()))

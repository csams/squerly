import logging
from subprocess import check_output
from queryable import Queryable

log = logging.getLogger(__name__)

_table = {
    "a": {"name": "access_mode", "type": str},
    "c": {"name": "command", "type": str},
    "C": {"name": "structure_share_count", "type": int},
    "d": {"name": "device_character_code", "type": str},
    "D": {"name": "device_number", "type": str},
    "f": {"name": "descriptor", "type": str},
    "F": {"name": "structure_address", "type": str},
    "G": {"name": "flags", "type": str},
    "g": {"name": "gid", "type": int},
    "i": {"name": "inode_number", "type": int},
    "K": {"name": "task_id", "type": int},
    "k": {"name": "link_count", "type": int},
    "l": {"name": "lock_status", "type": str},
    "L": {"name": "login_name", "type": str},
    "m": {"name": "repeated_output_marker", "type": str},
    "M": {"name": "task_command", "type": str},
    "n": {"name": "file_name", "type": str},
    "N": {"name": "node_identifier", "type": str},
    "o": {"name": "offset", "type": str},
    "p": {"name": "pid", "type": int},
    "P": {"name": "protocol_name", "type": str},
    "r": {"name": "raw_device_number", "type": str},
    "R": {"name": "ppid", "type": int},
    "s": {"name": "size", "type": int},
    "S": {"name": "stream", "type": str},
    "t": {"name": "type", "type": str},
    "TQR": {"name": "tcp_read_queue_size", "type": int},
    "TQS": {"name": "tcp_send_queue_size", "type": int},
    "TSO": {"name": "tcp_socket_options", "type": str},
    "TSS": {"name": "tcp_socket_states", "type": str},
    "TST": {"name": "tcp_connection_state", "type": str},
    "TTF": {"name": "tcp_flags", "type": str},
    "TWR": {"name": "tcp_window_read_size", "type": int},
    "TWS": {"name": "tcp_window_write_size", "type": int},
    "u": {"name": "uid", "type": int},
    "z": {"name": "zone_name", "type": str},
    "Z": {"name": "selinux_security_context", "type": str},
    "0": {"name": "use_nul_sep", "type": str},
    "1": {"name": "dialect_specific_1", "type": str},
    "2": {"name": "dialect_specific_2", "type": str},
    "3": {"name": "dialect_specific_3", "type": str},
    "4": {"name": "dialect_specific_4", "type": str},
    "5": {"name": "dialect_specific_5", "type": str},
    "6": {"name": "dialect_specific_6", "type": str},
    "7": {"name": "dialect_specific_7", "type": str},
    "8": {"name": "dialect_specific_8", "type": str},
    "9": {"name": "dialect_specific_9", "type": str},
}


def parse(content):
    results = []
    one = {}
    net = False
    for line in content:
        line = line.rstrip()

        if line.startswith("T"):
            k, v = line.split("=", 1)
            net = True
        else:
            k, v = line[0], line[1:]

        meta = _table.get(k)
        if not meta:
            log.warn(f"Skipping unknown key: %s", k)
            continue

        key, _type = meta["name"], meta["type"]
        # start a new record
        if key in one:
            # overloaded prefix
            if net and "file_name" in one:
                one["internet_address"] = one["file_name"]
                del one["file_name"]
            results.append(one)
            one = {}
            net = False

        one[key] = _type(v) if v != "" else None
    if one:
        results.append(one)

    return Queryable(results)


def load():
    return check_output(["lsof", "-F"], encoding="utf-8").splitlines()


def get():
    return parse(load())

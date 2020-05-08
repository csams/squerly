import logging
from subprocess import check_output
from queryable import Queryable

log = logging.getLogger(__name__)

_table = {
    "a": {"name": "access_mode", "type": str},
    "c": {"name": "process_command_name", "type": str},
    "C": {"name": "structure_share_count", "type": int},
    "d": {"name": "device_character_code", "type": str},
    "D": {"name": "device_number", "type": str},
    "f": {"name": "descriptor", "type": str},
    "F": {"name": "structure_address", "type": str},
    "G": {"name": "flags", "type": str},
    "g": {"name": "process_group_id", "type": int},
    "i": {"name": "inode_number", "type": int},
    "K": {"name": "task_id", "type": int},
    "k": {"name": "link_count", "type": int},
    "l": {"name": "lock_status", "type": str},
    "L": {"name": "process_login_name", "type": str},
    "m": {"name": "repeated_output_marker", "type": str},
    "M": {"name": "task_command_name", "type": str},
    "n": {"name": "file_name", "type": str},
    "N": {"name": "node_identifier", "type": str},
    "o": {"name": "offset", "type": str},
    "p": {"name": "process_id", "type": int},
    "P": {"name": "protocol_name", "type": str},
    "r": {"name": "raw_device_number", "type": str},
    "R": {"name": "parent_process_id", "type": int},
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
    "u": {"name": "process_user_id", "type": int},
    "z": {"name": "zone_name", "type": str},
    "Z": {"name": "selinux_security_context", "type": str},
    "0": {"name": "use_nul_sep", "type": str},
    "1": {"name": "1", "type": str},
    "2": {"name": "2", "type": str},
    "3": {"name": "3", "type": str},
    "4": {"name": "4", "type": str},
    "5": {"name": "5", "type": str},
    "6": {"name": "6", "type": str},
    "7": {"name": "7", "type": str},
    "8": {"name": "8", "type": str},
    "9": {"name": "9", "type": str},
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
            log.warn(f"Unknown key: {k}")
            continue

        key, _type = meta["name"], meta["type"]
        if key in one:
            if net:
                if "file_name" in one:
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

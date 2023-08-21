from datetime import datetime
from time import struct_time, mktime


def convert_time_struct_to_dt(struct: struct_time) -> datetime:
    return datetime.fromtimestamp(mktime(struct))

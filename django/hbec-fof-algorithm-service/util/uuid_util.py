import uuid


def gen_uuid():
    return str(uuid.uuid1()).replace("-", "")

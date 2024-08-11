import uuid


def get_uuid():
    return str(uuid.uuid4())


def get_8_random_str():
    return uuid.uuid4().hex[:8]

import uuid


def get_uuid():
    uhex = uuid.uuid4().hex
    snippet = "a" + uhex[:7]
    # TODO: Validate uniqueness of the uuid against the db
    return snippet

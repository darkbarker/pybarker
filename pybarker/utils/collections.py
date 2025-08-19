
def subdict(d: dict, keys) -> dict:
    """ sub-dict of d with keys only (intersect dictkeys+keys) """
    return {k: v for k, v in d.items() if k in keys}


def list_difference(x: list, y: list) -> list:
    """difference as exists for set, but for list (keep order)(a new instance)"""
    return [item for item in x if item not in y]

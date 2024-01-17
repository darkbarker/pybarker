
def subdict(d: dict, keys) -> dict:
    """ sub-dict of d with keys only (intersect dictkeys+keys) """
    return {k: v for k, v in d.items() if k in keys}

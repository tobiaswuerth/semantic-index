from functools import lru_cache

from ..manager import Manager


@lru_cache(maxsize=1)
def get_manager() -> Manager:
    return Manager()

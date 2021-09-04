from collections import OrderedDict, defaultdict
from collections.abc import Generator
from typing import Any

odict = OrderedDict
ddict = defaultdict


class AutoDict(dict):
    def __getitem__(self, key):
        ...

    def to_dict(self) -> dict:
        ...


class AutoOrderedDict(OrderedDict, AutoDict):
    ...


def dzip(items1, items2, cls=...):
    ...


def group_items(items, key):
    ...


def dict_hist(items,
              weights: Any | None = ...,
              ordered: bool = ...,
              labels: Any | None = ...):
    ...


def find_duplicates(items, k: int = ..., key: Any | None = ...):
    ...


def dict_subset(dict_, keys, default=..., cls=...):
    ...


def dict_union(*args):
    ...


def dict_diff(*args):
    ...


def dict_isect(*args):
    ...


def map_vals(func, dict_):
    ...


def map_keys(func, dict_):
    ...


def sorted_vals(dict_, key: Any | None = ..., reverse: bool = ...):
    ...


sorted_values = sorted_vals


def sorted_keys(dict_, key: Any | None = ..., reverse: bool = ...):
    ...


def invert_dict(dict_, unique_vals: bool = ...):
    ...


def named_product(_: Any | None = ..., **basis) -> Generator[Any, None, None]:
    ...


def varied_values(longform, min_variations: int = ..., default=...):
    ...

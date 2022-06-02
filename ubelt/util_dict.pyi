from typing import Iterable
from typing import Type
from typing import Dict
from typing import Callable
from typing import Union
from typing import List
from typing import Optional
from typing import Mapping
from typing import Set
from collections import OrderedDict, defaultdict
from collections.abc import Generator
from typing import Any, TypeVar
from ubelt import util_const

T = TypeVar("T")
VT = TypeVar("VT")
KT = TypeVar("KT")
odict = OrderedDict
ddict = defaultdict


class AutoDict(dict):

    def __getitem__(self, key):
        ...

    def to_dict(self) -> dict:
        ...


class AutoOrderedDict(OrderedDict, AutoDict):
    ...


def dzip(items1: Iterable[KT],
         items2: Iterable[VT],
         cls: Type[dict] = ...) -> Dict[KT, VT]:
    ...


def group_items(
        items: Iterable[VT],
        key: Union[Iterable[KT], Callable[[VT], KT]]) -> dict[KT, List[VT]]:
    ...


def dict_hist(items: Iterable[T],
              weights: Iterable[float] = ...,
              ordered: bool = ...,
              labels: Iterable[T] = ...) -> dict[T, int]:
    ...


def find_duplicates(items: Iterable[T],
                    k: int = ...,
                    key: Callable[[T], Any] = ...) -> dict[T, List[int]]:
    ...


def dict_subset(dict_: Dict[KT, VT],
                keys: Iterable[KT],
                default: Union[Optional[object],
                               util_const._NoParamType] = ...,
                cls: Type[Dict] = ...) -> Dict[KT, VT]:
    ...


def dict_union(*args: List[Dict]) -> Dict | OrderedDict:
    ...


def dict_diff(
    *args: List[Union[Dict[KT, VT], Iterable[KT]]]
) -> Dict[KT, VT] | OrderedDict[KT, VT]:
    ...


def dict_isect(
    *args: List[Union[Dict[KT, VT], Iterable[KT]]]
) -> Dict[KT, VT] | OrderedDict[KT, VT]:
    ...


def map_vals(func: Union[Callable[[VT], T], Mapping[VT, T]],
             dict_: Dict[KT, VT]) -> Dict[KT, T]:
    ...


def map_keys(func: Union[Callable[[KT], T], Mapping[KT, T]],
             dict_: Dict[KT, VT]) -> Dict[T, VT]:
    ...


def sorted_vals(dict_: Dict[KT, VT],
                key: Union[Callable[[VT], Any], None] = ...,
                reverse: bool = ...) -> OrderedDict[KT, VT]:
    ...


sorted_values = sorted_vals


def sorted_keys(dict_: Dict[KT, VT],
                key: Union[Callable[[KT], Any], None] = ...,
                reverse: bool = ...) -> OrderedDict[KT, VT]:
    ...


def invert_dict(dict_: Dict[KT, VT],
                unique_vals: bool = ...) -> Dict[VT, KT] | Dict[VT, Set[KT]]:
    ...


def named_product(
        _: Union[Dict[str, List[VT]], None] = ...,
        **basis: Dict[str, List[VT]]) -> Generator[Dict[str, VT], None, None]:
    ...


def varied_values(longform: List[Dict[KT, VT]],
                  min_variations: int = ...,
                  default: VT = ...) -> Dict[KT, List[VT]]:
    ...

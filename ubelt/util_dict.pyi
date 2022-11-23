from typing import Iterable
from typing import Type
from typing import Dict
from typing import Callable
from typing import Union
from typing import List
from typing import Optional
from ubelt.util_const import NoParamType
from typing import Mapping
from typing import Set
import sys
from collections import OrderedDict, defaultdict
from collections.abc import Generator
from typing import Any, TypeVar

VT = TypeVar("VT")
T = TypeVar("T")
KT = TypeVar("KT")
odict = OrderedDict
ddict = defaultdict
DictBase = OrderedDict if sys.version_info[0:2] <= (3, 6) else dict


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
                default: Union[Optional[object], NoParamType] = ...,
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


def map_values(func: Union[Callable[[VT], T], Mapping[VT, T]],
               dict_: Dict[KT, VT],
               cls: Union[type, None] = ...) -> Dict[KT, T]:
    ...


map_vals = map_values


def map_keys(func: Union[Callable[[KT], T], Mapping[KT, T]],
             dict_: Dict[KT, VT],
             cls: Union[type, None] = ...) -> Dict[T, VT]:
    ...


def sorted_values(dict_: Dict[KT, VT],
                  key: Union[Callable[[VT], Any], None] = ...,
                  reverse: bool = ...,
                  cls: type = ...) -> OrderedDict[KT, VT]:
    ...


sorted_vals = sorted_values


def sorted_keys(dict_: Dict[KT, VT],
                key: Union[Callable[[KT], Any], None] = ...,
                reverse: bool = ...,
                cls: type = ...) -> OrderedDict[KT, VT]:
    ...


def invert_dict(
        dict_: Dict[KT, VT],
        unique_vals: bool = ...,
        cls: Union[type, None] = ...) -> Dict[VT, KT] | Dict[VT, Set[KT]]:
    ...


def named_product(
        _: Union[Dict[str, List[VT]], None] = ...,
        **basis: Dict[str, List[VT]]) -> Generator[Dict[str, VT], None, None]:
    ...


def varied_values(longform: List[Dict[KT, VT]],
                  min_variations: int = ...,
                  default: Union[VT, NoParamType] = ...) -> Dict[KT, List[VT]]:
    ...


class SetDict(dict):

    def copy(self):
        ...

    def __or__(self, other):
        ...

    def __and__(self, other):
        ...

    def __sub__(self, other):
        ...

    def __xor__(self, other):
        ...

    def __ror__(self, other):
        ...

    def __rand__(self, other):
        ...

    def __rsub__(self, other):
        ...

    def __rxor__(self, other):
        ...

    def __ior__(self, other):
        ...

    def __iand__(self, other):
        ...

    def __isub__(self, other):
        ...

    def __ixor__(self, other):
        ...

    def union(self, *others, cls: type = ...) -> dict:
        ...

    def intersection(self, *others, cls: type = ...) -> dict:
        ...

    def difference(self, *others, cls: type = ...) -> dict:
        ...

    def symmetric_difference(self, *others, cls: type = ...) -> dict:
        ...


sdict = SetDict


class UDict(SetDict):

    def subdict(self,
                keys: Iterable[KT],
                default: Union[Optional[object], NoParamType] = ...):
        ...

    def take(
        self,
        keys: Iterable[KT],
        default: Union[Optional[object], NoParamType] = ...
    ) -> Generator[VT, None, None]:
        ...

    def invert(self,
               unique_vals: bool = ...) -> Dict[VT, KT] | Dict[VT, Set[KT]]:
        ...

    def map_keys(
            self, func: Union[Callable[[VT], T], Mapping[VT,
                                                         T]]) -> Dict[KT, T]:
        ...

    def map_values(
            self, func: Union[Callable[[VT], T], Mapping[VT,
                                                         T]]) -> Dict[KT, T]:
        ...

    def sorted_keys(self,
                    key: Union[Callable[[KT], Any], None] = ...,
                    reverse: bool = ...) -> OrderedDict[KT, VT]:
        ...

    def sorted_values(self,
                      key: Union[Callable[[VT], Any], None] = ...,
                      reverse: bool = ...) -> OrderedDict[KT, VT]:
        ...

    def peek_key(self, default: Union[KT, NoParamType] = ...) -> KT:
        ...

    def peek_value(self, default: Union[VT, NoParamType] = ...) -> VT:
        ...


class AutoDict(UDict):

    def __getitem__(self, key):
        ...

    def to_dict(self) -> dict:
        ...


AutoOrderedDict = AutoDict
udict = UDict

import sys
from typing import Iterable
from typing import Type
from typing import Dict
from typing import Callable
from typing import List
from typing import Any
from typing import Optional
from ubelt.util_const import NoParam
from ubelt.util_const import NoParamType
from collections import OrderedDict
from typing import Mapping
from typing import Set
from typing import Tuple
from _typeshed import SupportsKeysAndGetItem
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
         cls: Type[dict] = dict) -> Dict[KT, VT]:
    ...


def group_items(items: Iterable[VT],
                key: Iterable[KT] | Callable[[VT], KT]) -> dict[KT, List[VT]]:
    ...


def dict_hist(items: Iterable[T],
              weights: Iterable[float] | None = None,
              ordered: bool = False,
              labels: Iterable[T] | None = None) -> dict[T, int]:
    ...


def find_duplicates(
        items: Iterable[T],
        k: int = 2,
        key: Callable[[T], Any] | None = None) -> dict[T, List[int]]:
    ...


def dict_subset(dict_: Dict[KT, VT],
                keys: Iterable[KT],
                default: Optional[object] | NoParamType = NoParam,
                cls: Type[Dict] = OrderedDict) -> Dict[KT, VT]:
    ...


def dict_union(*args: List[Dict]) -> Dict | OrderedDict:
    ...


def dict_diff(
    *args: List[Dict[KT, VT] | Iterable[KT]]
) -> Dict[KT, VT] | OrderedDict[KT, VT]:
    ...


def dict_isect(
    *args: List[Dict[KT, VT] | Iterable[KT]]
) -> Dict[KT, VT] | OrderedDict[KT, VT]:
    ...


def map_values(func: Callable[[VT], T] | Mapping[VT, T],
               dict_: Dict[KT, VT],
               cls: type | None = None) -> Dict[KT, T]:
    ...


map_vals = map_values


def map_keys(func: Callable[[KT], T] | Mapping[KT, T],
             dict_: Dict[KT, VT],
             cls: type | None = None) -> Dict[T, VT]:
    ...


def sorted_values(dict_: Dict[KT, VT],
                  key: Callable[[VT], Any] | None = None,
                  reverse: bool = False,
                  cls: type = OrderedDict) -> OrderedDict[KT, VT]:
    ...


sorted_vals = sorted_values


def sorted_keys(dict_: Dict[KT, VT],
                key: Callable[[KT], Any] | None = None,
                reverse: bool = False,
                cls: type = OrderedDict) -> OrderedDict[KT, VT]:
    ...


def invert_dict(dict_: Dict[KT, VT],
                unique_vals: bool = True,
                cls: type | None = None) -> Dict[VT, KT] | Dict[VT, Set[KT]]:
    ...


def named_product(
        _: Dict[str, List[VT]] | None = None,
        **basis: Dict[str, List[VT]]) -> Generator[Dict[str, VT], None, None]:
    ...


def varied_values(longform: List[Dict[KT, VT]],
                  min_variations: int = 0,
                  default: VT | NoParamType = NoParam) -> Dict[KT, List[VT]]:
    ...


class SetDict(dict):

    def copy(self):
        ...

    def __or__(
        self,
        other: SupportsKeysAndGetItem[Any, Any] | Iterable[Tuple[Any, Any]]
    ) -> SetDict:
        ...

    def __and__(self, other: Mapping | Iterable) -> SetDict:
        ...

    def __sub__(self, other: Mapping | Iterable) -> SetDict:
        ...

    def __xor__(self, other: Mapping) -> SetDict:
        ...

    def __ror__(self, other: Mapping) -> dict:
        ...

    def __rand__(self, other: Mapping) -> dict:
        ...

    def __rsub__(self, other: Mapping) -> dict:
        ...

    def __rxor__(self, other: Mapping) -> dict:
        ...

    def __ior__(
        self,
        other: SupportsKeysAndGetItem[Any, Any] | Iterable[Tuple[Any, Any]]
    ) -> SetDict:
        ...

    def __iand__(self, other: Mapping | Iterable):
        ...

    def __isub__(self, other: Mapping | Iterable):
        ...

    def __ixor__(self, other: Mapping):
        ...

    def union(self,
              *others,
              cls: type | None = None,
              merge: None | Callable = None) -> dict:
        ...

    def intersection(self,
                     *others,
                     cls: type | None = None,
                     merge: None | Callable = None) -> dict:
        ...

    def difference(self,
                   *others,
                   cls: type | None = None,
                   merge: None | Callable = None) -> dict:
        ...

    def symmetric_difference(self,
                             *others,
                             cls: type | None = None,
                             merge: None | Callable = None) -> dict:
        ...


sdict = SetDict


class UDict(SetDict):

    def subdict(self,
                keys: Iterable[KT],
                default: Optional[object] | NoParamType = NoParam):
        ...

    def take(
        self,
        keys: Iterable[KT],
        default: Optional[object] | NoParamType = NoParam
    ) -> Generator[VT, None, None]:
        ...

    def invert(self,
               unique_vals: bool = True) -> Dict[VT, KT] | Dict[VT, Set[KT]]:
        ...

    def map_keys(self,
                 func: Callable[[VT], T] | Mapping[VT, T]) -> Dict[KT, T]:
        ...

    def map_values(self,
                   func: Callable[[VT], T] | Mapping[VT, T]) -> Dict[KT, T]:
        ...

    def sorted_keys(self,
                    key: Callable[[KT], Any] | None = None,
                    reverse: bool = False) -> OrderedDict[KT, VT]:
        ...

    def sorted_values(self,
                      key: Callable[[VT], Any] | None = None,
                      reverse: bool = False) -> OrderedDict[KT, VT]:
        ...

    def peek_key(self, default: KT | NoParamType = NoParam) -> KT:
        ...

    def peek_value(self, default: VT | NoParamType = NoParam) -> VT:
        ...


class AutoDict(UDict):

    def __getitem__(self, key: KT) -> VT | AutoDict:
        ...

    def to_dict(self) -> dict:
        ...


AutoOrderedDict = AutoDict
udict = UDict

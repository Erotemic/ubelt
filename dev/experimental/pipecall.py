"""
I want a way to cast to a list without having to backspace.
This is a way to do it. But at what cost?
"""


class RorListType(type):
    cls = list

    @classmethod
    def __ror__(mcls, obj):
        return mcls.cls(obj)

    @classmethod
    def __or__(mcls, obj):
        return mcls.cls(obj)


class RorList(RorListType.cls, metaclass=RorListType):
    """
    Example:
        >>> iter(range(5)) | RorList
        [0, 1, 2, 3, 5]

        >>> L = RorList
        >>> range(3) | L
        [0, 1, 2]
    """
    ...

class NoParamType:

    def __new__(cls):
        ...

    def __reduce__(self):
        ...

    def __copy__(self):
        ...

    def __deepcopy__(self, memo):
        ...

    def __bool__(self):
        ...


NoParam: NoParamType

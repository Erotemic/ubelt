"""
POC google docstring plugin for mypy
"""

from typing import Callable, Optional

from mypy.plugin import FunctionSigContext, Plugin
from mypy.types import CallableType


class CustomPlugin(Plugin):
    """

    cd $HOME/code/ubelt
    mypy -m ubelt.util_dict
    stubgen -m ubelt.util_dict

    """

    # def get_type_analyze_hook(self, fullname: str):
    #     print('get_type_analyze_hook: fullname = {!r}'.format(fullname))

    def get_function_signature_hook(
        self, fullname: str
    ) -> Optional[Callable[[FunctionSigContext], CallableType]]:
        """Adjust the signature of a function.

        This method is called before type checking a function call. Plugin
        may infer a better type for the function.

            from lib import Class, do_stuff

            do_stuff(42)
            Class()

        This method will be called with 'lib.do_stuff' and then with 'lib.Class'.
        """
        if 'ubelt' in fullname or 'util_' in fullname:
            print(
                'get_function_signature_hook: fullname = {!r}'.format(fullname)
            )
        return None


def plugin(version: str):
    # ignore version argument if the plugin works with all mypy versions.
    return CustomPlugin

"""
This is a specialized set of tests for the util_import module on editable
installs, specifically with the new setuptools editable hooks (v64.0.0).
https://setuptools.pypa.io/en/latest/userguide/development_mode.html
https://setuptools.pypa.io/en/latest/history.html#id37

Running the setup and teardown for this test is very expensive wrt how long
this test takes versus others in this library.
We should look into if there is a cheaper way to emulate it.
What we could do is run the expensive test once, and serialize the outputs it
produces so we can simply reconstruct the environment.
"""
import os
import sys


class ProjectStructure():
    """
    Method to help setup and teardown a demo package installed in editable
    mode.

    Ignore:
        import ubelt as ub
        import sys, ubelt
        import xdev
        sys.path.append(ubelt.expandpath('~/code/ubelt/tests'))
        from test_editable_modules import *  # NOQA
        dpath = ub.Path.appdir('ubelt/tests/demo_project').ensuredir()
        self = ProjectStructure(dpath, mod_name='demopkg_mwe', use_src=False)
        self.generate()
        self.analyze()
        self.install()

    """
    def __init__(self, repo_dpath='.', mod_name='demopkg_mwe', use_src=True):
        import ubelt as ub
        self.root = ub.Path(repo_dpath)
        self.mod_name = mod_name
        self.use_src = use_src
        if use_src:
            self.python_relpath = ub.Path('src', 'python')
        else:
            self.python_relpath = ub.Path('.')
        self.cxx_relpath = ub.Path('src', 'cxx')
        self.cxx_path    = (self.root / self.cxx_relpath)
        self.python_path = (self.root / self.python_relpath)
        self.mod_dpath = (self.python_path / self.mod_name)

    def setup(self):
        self.generate()
        self.install()

    def teardown(self):
        self.uninstall()
        self.delete()

    def install(self):
        import sys
        import ubelt as ub
        ub.cmd([sys.executable, '-m', 'pip', 'install', '-e', self.root],
               verbose=3, check=True)

    def delete(self):
        self.root.delete()

    def uninstall(self):
        import sys
        import ubelt as ub
        ub.cmd([sys.executable, '-m', 'pip', 'uninstall', self.mod_name, '-y'],
               verbose=3, check=True)

    def generate(self, with_cxx=0):
        import ubelt as ub
        self.mod_dpath.delete().ensuredir()
        self.cxx_path.delete()
        (self.root / 'CMakeLists.txt').delete()
        (self.mod_dpath / '__init__.py').write_text('__version__ = "1.0.0"')

        if self.use_src:
            package_dir_line = ub.codeblock(
                f'''
                package_dir={{'': '{self.python_relpath}'}},
                ''')
        else:
            package_dir_line = ''

        # Give the MWE a CXX extension
        WITH_CXX = with_cxx
        if WITH_CXX:
            (self.root / 'pyproject.toml').write_text(ub.codeblock(
                '''
                [build-system]
                requires = ["setuptools>=41.0.1", "scikit-build>=0.11.1", "numpy", "ninja>=1.10.2", "cmake>=3.21.2", "cython>=0.29.24",]
                '''))
            (self.root / 'setup.py').write_text(ub.codeblock(
                f'''
                if __name__ == '__main__':
                    from skbuild import setup
                    from setuptools import find_packages
                    packages = find_packages('./{self.python_relpath}')
                    setup(
                        {package_dir_line}
                        install_requires=['packaging'],
                        name='{self.mod_name}',
                        version="1.0.0",
                        description='MWE of a binpy project',
                        packages=packages,
                        include_package_data=True,
                    )
                '''))
            self.cxx_path.ensuredir()
            (self.root / 'CMakeLists.txt').write_text(ub.codeblock(
                rf'''
                cmake_minimum_required(VERSION 3.13.0)
                project({self.mod_name} LANGUAGES C Fortran)

                find_package(PythonInterp REQUIRED)
                find_package(PythonLibs REQUIRED)

                ###
                # Private helper function to execute `python -c "<cmd>"`
                #
                # Runs a python command and populates an outvar with the result of stdout.
                # Be careful of indentation if `cmd` is multiline.
                #
                function(pycmd outvar cmd)
                  execute_process(
                    COMMAND "${{PYTHON_EXECUTABLE}}" -c "${{{{cmd}}}}"
                    RESULT_VARIABLE _exitcode
                    OUTPUT_VARIABLE _output)
                  if(NOT ${{_exitcode}} EQUAL 0)
                    message(ERROR "Failed when running python code: \"\"\"
                ${{cmd}}\"\"\"")
                    message(FATAL_ERROR "Python command failed with error code: ${{_exitcode}}")
                  endif()
                  # Remove supurflous newlines (artifacts of print)
                  string(STRIP "${{_output}}" _output)
                  set(${{outvar}} "${{_output}}" PARENT_SCOPE)
                endfunction()

                ###
                # Find scikit-build and include its cmake resource scripts
                #
                if (NOT SKBUILD)
                  pycmd(skbuild_location "import os, skbuild; print(os.path.dirname(skbuild.__file__))")
                  set(skbuild_cmake_dir "${{skbuild_location}}/resources/cmake")
                  # If skbuild is not the driver, then we need to include its utilities in our CMAKE_MODULE_PATH
                  list(APPEND CMAKE_MODULE_PATH ${{skbuild_cmake_dir}})
                endif()

                find_package(PythonExtensions REQUIRED)
                find_package(Cython REQUIRED)
                find_package(NumPy REQUIRED)

                # Backend C library
                add_subdirectory("src/cxx")

                # Cython library
                add_subdirectory("src/python/{self.mod_name}")
                '''))

            (self.cxx_path / 'myalgo.h').write_text(ub.codeblock(
                '''
                #ifndef MYALGO_H
                #define MYALGO_H
                int myalgo(long *arr1, long *arr2, size_t num);
                #endif MYALGO_H
                '''))
            (self.cxx_path / 'myalgo.c').write_text(ub.codeblock(
                r'''
                #include <string.h>
                long myalgo(long *arr1, long *arr2, size_t num)
                {
                    for (int i = 0 ; i < num ; i++ )
                    {
                        arr2[i] = arr1[i] + arr2[i];
                    }
                    return 1;
                }
                '''))
            cmake_list_cxx = self.cxx_path / 'CMakeLists.txt'
            cmake_list_cxx.write_text(ub.codeblock(
                '''
                set(MYALGO_MODULE_NAME "myalgo")
                list(APPEND MYALGO_SOURCES "myalgo.h" "myalgo.c")
                add_library(${MYALGO_MODULE_NAME} STATIC ${MYALGO_SOURCES})
                '''))

            (self.mod_dpath / 'myalgo_cython.pyx').write_text(ub.codeblock(
                '''
                import numpy as np
                cimport numpy as np
                cdef extern from "../../cxx/myalgo.h":
                    cdef int myalgo(long *arr1, long *arr2, size_t num);

                def call_myalgo():
                    """
                    This is a docstring
                    """
                    cdef int result;
                    cdef np.ndarray[np.int64_t, ndim=1] arr1
                    cdef np.ndarray[np.int64_t, ndim=1] arr2
                    arr1 = np.array([1, 2, 3], dtype=np.int64)
                    arr2 = np.array([4, 6, 9], dtype=np.int64)
                    cdef long [:] arr1_view = arr1
                    cdef long [:] arr2_view = arr2
                    cdef size_t num = len(arr1)
                    print(f'arr1={arr1}')
                    print(f'arr2={arr2}')
                    print('calling my algo')
                    result = myalgo(&arr1_view[0], &arr2_view[0], num)
                    print(f'arr1={arr1}')
                    print(f'arr2={arr2}')
                    return result
                '''))

            (self.mod_dpath / 'CMakeLists.txt').write_text(ub.codeblock(
                '''
                set(cython_source "myalgo_cython.pyx")
                set(PYMYALGO_MODULE_NAME "myalgo_cython")

                # Translate Cython into C/C++
                add_cython_target(${PYMYALGO_MODULE_NAME} "${cython_source}" C OUTPUT_VAR sources)

                # Add other C sources
                list(APPEND sources )

                # Create C++ library. Specify include dirs and link libs as normal
                add_library(${PYMYALGO_MODULE_NAME} MODULE ${sources})
                target_include_directories(
                    ${PYMYALGO_MODULE_NAME}
                    PUBLIC
                    ${NumPy_INCLUDE_DIRS}
                    ${PYTHON_INCLUDE_DIR}
                    ${CMAKE_CURRENT_SOURCE_DIR}
                )

                # TODO: not sure why this isn't set in the global scope?
                # Hack around it: just hard code the module name
                set(MYALGO_MODULE_NAME "myalgo")

                # TODO: linking to the MYALGO shared object isn't working 100% yet.
                target_link_libraries(${PYMYALGO_MODULE_NAME} ${MYALGO_MODULE_NAME})

                target_compile_definitions(${PYMYALGO_MODULE_NAME} PUBLIC
                    "NPY_NO_DEPRECATED_API"
                    #"NPY_1_7_API_VERSION=0x00000007"
                )

                # Transform the C++ library into an importable python module
                python_extension_module(${PYMYALGO_MODULE_NAME})

                # Install the C++ module to the correct relative location
                # (this will be an inplace build if you use `pip install -e`)
                #file(RELATIVE_PATH pymyalgo_install_dest "${CMAKE_SOURCE_DIR}" "${CMAKE_CURRENT_SOURCE_DIR}")

                # My "normal" method of setting install targets does not seem to work here. Hacking it.
                # NOTE: skbuild *seems* to place libraries in a data dir *unless* the install destination
                # corresponds exactly to the <package_dir>/<package_name> specified implicitly in setup.py
                set(pymyalgo_install_dest "src/python/{self.mod_name}")
                #install(TARGETS ${MYALGO_MODULE_NAME} LIBRARY DESTINATION "${pymyalgo_install_dest}")
                install(TARGETS ${PYMYALGO_MODULE_NAME} LIBRARY DESTINATION "${pymyalgo_install_dest}")
                '''
            ))
        else:
            # Pure Python
            # TODO: Might want to test with different build backends.
            (self.root / 'pyproject.toml').write_text(ub.codeblock(
                '''
                [build-system]
                requires = ["setuptools>=41.0.1", "wheel"]
                build-backend = "setuptools.build_meta"
                '''))
            (self.root / 'setup.py').write_text(ub.codeblock(
                f'''
                if __name__ == '__main__':
                    from setuptools import setup
                    from setuptools import find_packages
                    packages = find_packages('./{self.python_relpath}')
                    setup(
                        {package_dir_line}
                        package_data={{
                            '{self.mod_name}': ['py.typed', '*.pyi'],
                        }},
                        install_requires=['packaging'],
                        name='{self.mod_name}',
                        version="1.0.0",
                        description='MWE of a purepy project',
                        packages=packages,
                        include_package_data=True,
                    )
                '''))
            (self.mod_dpath / 'py.typed').write_text('')
            (self.mod_dpath / 'submod.py').write_text('A = 1')
            (self.mod_dpath / 'submod.pyi').write_text('A: int')

    def analyze(self):
        """
        For debugging and develoment only, don't run in the tests

        Requires:
            rich, xdev
        """
        from rich.console import Console
        from rich.panel import Panel
        from rich.syntax import Syntax
        from rich.table import Table
        import distutils.sysconfig
        import ubelt as ub
        import xdev

        console = Console()

        def rich_file_content(fpath, lexer='bash'):
            import os
            text = fpath.read_text()
            return Panel(Syntax(text, lexer), title=os.fspath(fpath))

        def print_egg_path_content(egg_info_dpath, color='blue'):
            blocklist = {'requires.txt'}
            fpaths = egg_info_dpath.ls()
            table = Table(f'[{color}]' + str(egg_info_dpath))
            for fpath in fpaths:
                if fpath.name not in blocklist:
                    panel = rich_file_content(fpath)
                    table.add_row(panel)
            console.print(table)

        print('\n')
        print('Repo Structure:')
        directory_blocklist = ['.*', '.git', 'dist', '_skbuild', 'dev']
        xdev.tree_repr(self.root, max_files=None, dirblocklist=directory_blocklist)

        seems_installed = 0

        print('\n')
        print('Content of the EGG Link:')
        site_dpath = ub.Path(distutils.sysconfig.get_python_lib())
        egg_link_fpaths = list(site_dpath.glob(self.mod_name.replace('_', '*') + '*.egg-link'))
        if len(egg_link_fpaths) == 0:
            console.print('[red] No egg link')
            seems_installed = 0
        else:
            assert len(egg_link_fpaths) == 1
            egg_link_fpath = egg_link_fpaths[0]
            console.print(rich_file_content(egg_link_fpath))
            seems_installed = 1

        # Note: (recently 2022-08-ish) python switched to a new type of
        # This is not present in setuptools==63.2.0 but is in 65.3.0
        # editable install. TODO: incomporate this.
        editable_fpaths = list(site_dpath.glob('__editable__*' + self.mod_name.replace('_', '*') + '*'))
        print(f'editable_fpaths={editable_fpaths}')

        print('\n')
        print('Check easy-install.pth')
        easy_install_fpath = site_dpath / 'easy-install.pth'
        assert easy_install_fpath.exists()
        easy_install_text = easy_install_fpath.read_text()
        abs_path = self.mod_dpath.absolute().parent
        print(f'abs_path={abs_path}')
        if str(abs_path)  in easy_install_text:
            console.print('[green] Easy install dpath is good')
        else:
            console.print('[red] Easy install does not contain this package')
            # console.print(rich_file_content(easy_install_fpath))

        expected_egg_info_dpath = self.python_path / f'{self.mod_name}.egg-info'
        all_egg_infos = [ub.Path(e).resolve() for e in xdev.find('*.egg-info', dpath=self.root, dirblocklist=directory_blocklist)]
        other_egg_infos = set(all_egg_infos) - {expected_egg_info_dpath.resolve()}
        print('expected_egg_info_dpath = {}'.format(ub.repr2(expected_egg_info_dpath, nl=1)))
        if expected_egg_info_dpath.exists():
            console.print('[green] Egg info exists in expected location')
            egg_info_dpath = expected_egg_info_dpath
            print_egg_path_content(egg_info_dpath, color='green')
        else:
            console.print('[red] Egg info does not exist in expected location')
            print(f'other_egg_infos={other_egg_infos}')

        if other_egg_infos:
            console.print('[red] THERE ARE UNEXEPCTED EGG INFOS')
            for egg_info_dpath in other_egg_infos:
                print_egg_path_content(egg_info_dpath, color='red')

        if seems_installed:
            print('\n')
            print('Test to ensure we can import the module')
            command = f'python -c "import {self.mod_name}; print({self.mod_name})"'
            info = ub.cmd(command, verbose=3)
            if info['ret'] != 0:
                raise Exception('failed to import')
            assert str(self.mod_dpath) in info['out']
        else:
            console.print('[yellow] Package does not seem installed, so skipping import test')

    def serialize_install(self):
        # TODO: serialize this step to make it fast
        import distutils.sysconfig
        import ubelt as ub
        site_dpath = ub.Path(distutils.sysconfig.get_python_lib())
        egg_link_fpaths = list(site_dpath.glob(self.mod_name.replace('_', '*') + '*.egg-link'))
        editable_fpaths = list(site_dpath.glob('__editable__*' + self.mod_name.replace('_', '*') + '*'))
        easy_install_fpath = site_dpath / 'easy-install.pth'  # NOQA
        print(f'egg_link_fpaths={egg_link_fpaths}')
        print(f'editable_fpaths={editable_fpaths}')


GLOBAL_PROJECTS = []


def _check_skip_editable_module_tests():
    UBELT_DO_EDITABLE_TESTS = os.environ.get('UBELT_DO_EDITABLE_TESTS', '')
    if not UBELT_DO_EDITABLE_TESTS:
        import pytest
        pytest.skip('UBELT_DO_EDITABLE_TESTS is not enabled')

    if sys.platform.startswith('win32'):
        import pytest
        pytest.skip('skip editable module tests on Win32')

    if sys.platform.startswith('freebsd'):
        import pytest
        pytest.skip('skip editable module tests on FreeBSD')


def setup_module(module):
    """ setup any state specific to the execution of the given module."""
    import uuid
    import ubelt as ub

    _check_skip_editable_module_tests()

    suffix = ub.hash_data(uuid.uuid4(), base='abc')[0:8]
    dpath = ub.Path.appdir('ubelt/tests/demo_packages').ensuredir()

    # Define pure python module with ./src/python structure
    mod_name = 'purepy_src_demo_pkg_' + suffix
    PUREPY_SRC_PROJECT = ProjectStructure(repo_dpath=dpath / mod_name,
                                          mod_name=mod_name, use_src=True)
    PUREPY_SRC_PROJECT.setup()
    GLOBAL_PROJECTS.append(PUREPY_SRC_PROJECT)

    if 0:
        self = PUREPY_SRC_PROJECT
        self.serialize()

    # Define pure python module with the package at root level
    mod_name = 'purepy_root_demo_pkg_' + suffix
    PUREPY_SRC_PROJECT = ProjectStructure(repo_dpath=dpath / mod_name,
                                          mod_name=mod_name, use_src=False)
    PUREPY_SRC_PROJECT.setup()
    GLOBAL_PROJECTS.append(PUREPY_SRC_PROJECT)

    if 0:
        for proj in GLOBAL_PROJECTS:
            proj.analyze()


def teardown_module(module):
    """ teardown any state that was previously setup with a setup_module
    method.
    """
    _check_skip_editable_module_tests()
    for PROJ in GLOBAL_PROJECTS:
        PROJ.teardown()


def test_import_of_editable_install():
    _check_skip_editable_module_tests()
    import ubelt as ub
    for PROJ in GLOBAL_PROJECTS:
        result = ub.modname_to_modpath(PROJ.mod_name)
        print(f'result={result}')
        assert result is not None
        assert PROJ.mod_dpath == ub.Path(result)

"""
Liberated portions of :mod:`jaraco.windows.filesystem`.

Ignore:

    cat ~/code/ubelt/ubelt/_win32_links.py | grep -o jwfs.api
    cat ~/code/ubelt/ubelt/_win32_links.py | grep -o "jwfs\\.[^ ]*" | sort

    git clone git@github.com:jaraco/jaraco.windows.git $HOME/code
    cd ~/code/jaraco.windows
    touch jaraco/__init__.py

    ---

    Notes:
        liberator does not handle the ctypes attributes nicely where
        the definition is then modified with argtypes and restypes

        But it does help get a good start on the file.

    ---

    import liberator
    import ubelt as ub
    repo_dpath = ub.Path('~/code/jaraco.windows').expand()
    jwfs_modpath = repo_dpath / 'jaraco/windows/filesystem/__init__.py'
    jw_api_filesystem_modpath = repo_dpath / 'jaraco/windows/api/filesystem.py'
    jw_reparse_modpath = repo_dpath / 'jaraco/windows/reparse.py'

    lib = liberator.Liberator()
    lib.add_static('link', modpath=jwfs_modpath)
    lib.add_static('handle_nonzero_success', modpath=jwfs_modpath)
    lib.add_static('is_reparse_point', modpath=jwfs_modpath)

    # FIXME: argtypes / restypes
    lib.add_static('CreateFile', modpath=jw_api_filesystem_modpath)
    lib.add_static('CloseHandle', modpath=jw_api_filesystem_modpath)

    lib.add_static('REPARSE_DATA_BUFFER', modpath=jw_api_filesystem_modpath)
    lib.add_static('OPEN_EXISTING', modpath=jw_api_filesystem_modpath)
    lib.add_static('FILE_FLAG_OPEN_REPARSE_POINT', modpath=jw_api_filesystem_modpath)
    lib.add_static('FILE_FLAG_BACKUP_SEMANTICS', modpath=jw_api_filesystem_modpath)
    lib.add_static('FSCTL_GET_REPARSE_POINT', modpath=jw_api_filesystem_modpath)
    lib.add_static('INVALID_HANDLE_VALUE', modpath=jw_api_filesystem_modpath)
    lib.add_static('IO_REPARSE_TAG_SYMLINK', modpath=jw_api_filesystem_modpath)
    lib.add_static('BY_HANDLE_FILE_INFORMATION', modpath=jw_api_filesystem_modpath)
    lib.add_static('GetFileInformationByHandle', modpath=jw_api_filesystem_modpath)

    #lib.add_static('DeviceIoControl', modpath=jw_reparse_modpath)

    lib.expand(['jaraco'])

    print(lib.current_sourcecode())
"""


import ctypes
import ctypes.wintypes

# Makes mypy happy
import sys

assert sys.platform == "win32"


def handle_nonzero_success(result):
    if (result == 0):
        raise ctypes.WinError()


class BY_HANDLE_FILE_INFORMATION(ctypes.Structure):
    _fields_ = [
        ('file_attributes', ctypes.wintypes.DWORD),
        ('creation_time', ctypes.wintypes.FILETIME),
        ('last_access_time', ctypes.wintypes.FILETIME),
        ('last_write_time', ctypes.wintypes.FILETIME),
        ('volume_serial_number', ctypes.wintypes.DWORD),
        ('file_size_high', ctypes.wintypes.DWORD),
        ('file_size_low', ctypes.wintypes.DWORD),
        ('number_of_links', ctypes.wintypes.DWORD),
        ('file_index_high', ctypes.wintypes.DWORD),
        ('file_index_low', ctypes.wintypes.DWORD)
    ]

    @property
    def file_size(self):
        return ((self.file_size_high << 32) + self.file_size_low)

    @property
    def file_index(self):
        return ((self.file_index_high << 32) + self.file_index_low)


class REPARSE_DATA_BUFFER(ctypes.Structure):
    _fields_ = [
        ('tag', ctypes.c_ulong),
        ('data_length', ctypes.c_ushort),
        ('reserved', ctypes.c_ushort),
        ('substitute_name_offset', ctypes.c_ushort),
        ('substitute_name_length', ctypes.c_ushort),
        ('print_name_offset', ctypes.c_ushort),
        ('print_name_length', ctypes.c_ushort),
        ('flags', ctypes.c_ulong),
        ('path_buffer', (ctypes.c_byte * 1))
    ]

    def get_print_name(self):
        wchar_size = ctypes.sizeof(ctypes.wintypes.WCHAR)
        arr_typ = (ctypes.wintypes.WCHAR * (self.print_name_length // wchar_size))
        data = ctypes.byref(self.path_buffer, self.print_name_offset)
        return ctypes.cast(data, ctypes.POINTER(arr_typ)).contents.value

    def get_substitute_name(self):
        wchar_size = ctypes.sizeof(ctypes.wintypes.WCHAR)
        arr_typ = (ctypes.wintypes.WCHAR * (self.substitute_name_length // wchar_size))
        data = ctypes.byref(self.path_buffer, self.substitute_name_offset)
        return ctypes.cast(data, ctypes.POINTER(arr_typ)).contents.value


class SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = (
        ('length', ctypes.wintypes.DWORD),
        ('p_security_descriptor', ctypes.wintypes.LPVOID),
        ('inherit_handle', ctypes.wintypes.BOOLEAN),
    )

LPSECURITY_ATTRIBUTES = ctypes.POINTER(SECURITY_ATTRIBUTES)


IO_REPARSE_TAG_SYMLINK = 0xA000000C
INVALID_HANDLE_VALUE = ctypes.wintypes.HANDLE((- 1)).value
FSCTL_GET_REPARSE_POINT = 0x900A8
FILE_FLAG_BACKUP_SEMANTICS = 0x2000000
FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
FILE_SHARE_READ = 1
OPEN_EXISTING = 3


FILE_ATTRIBUTE_REPARSE_POINT = 0x400
GENERIC_READ = 0x80000000
INVALID_FILE_ATTRIBUTES = 0xFFFFFFFF

GetFileAttributes = ctypes.windll.kernel32.GetFileAttributesW
GetFileAttributes.argtypes = (ctypes.wintypes.LPWSTR,)
GetFileAttributes.restype = ctypes.wintypes.DWORD

CreateHardLink = ctypes.windll.kernel32.CreateHardLinkW
CreateHardLink.argtypes = (
    ctypes.wintypes.LPWSTR,
    ctypes.wintypes.LPWSTR,
    ctypes.wintypes.LPVOID,  # reserved for LPSECURITY_ATTRIBUTES
)
CreateHardLink.restype = ctypes.wintypes.BOOLEAN

GetFileInformationByHandle = ctypes.windll.kernel32.GetFileInformationByHandle
GetFileInformationByHandle.restype = ctypes.wintypes.BOOL
GetFileInformationByHandle.argtypes = (
    ctypes.wintypes.HANDLE,
    ctypes.POINTER(BY_HANDLE_FILE_INFORMATION),
)

CloseHandle = ctypes.windll.kernel32.CloseHandle
CloseHandle.argtypes = (ctypes.wintypes.HANDLE,)
CloseHandle.restype = ctypes.wintypes.BOOLEAN

CreateFile = ctypes.windll.kernel32.CreateFileW
CreateFile.argtypes = (
    ctypes.wintypes.LPWSTR,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.DWORD,
    LPSECURITY_ATTRIBUTES,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.HANDLE,
)
CreateFile.restype = ctypes.wintypes.HANDLE

LPDWORD = ctypes.POINTER(ctypes.wintypes.DWORD)
LPOVERLAPPED = ctypes.wintypes.LPVOID

DeviceIoControl = ctypes.windll.kernel32.DeviceIoControl
DeviceIoControl.argtypes = [
    ctypes.wintypes.HANDLE,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.LPVOID,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.LPVOID,
    ctypes.wintypes.DWORD,
    LPDWORD,
    LPOVERLAPPED,
]
DeviceIoControl.restype = ctypes.wintypes.BOOL


def is_reparse_point(path):
    """
    Determine if the given path is a reparse point.
    Return False if the file does not exist or the file attributes cannot
    be determined.
    """
    res = GetFileAttributes(path)
    return ((res != INVALID_FILE_ATTRIBUTES) and bool((res & FILE_ATTRIBUTE_REPARSE_POINT)))


def link(target, link):
    """
    Establishes a hard link between an existing file and a new file.
    """
    handle_nonzero_success(CreateHardLink(link, target, None))


def _reparse_DeviceIoControl(device, io_control_code, in_buffer, out_buffer, overlapped=None):
    # ubelt note: name is overloaded, so we mangle it here.
    if overlapped is not None:
        raise NotImplementedError("overlapped handles not yet supported")

    if isinstance(out_buffer, int):
        out_buffer = ctypes.create_string_buffer(out_buffer)

    in_buffer_size = len(in_buffer) if in_buffer is not None else 0
    out_buffer_size = len(out_buffer)
    assert isinstance(out_buffer, ctypes.Array)

    returned_bytes = ctypes.wintypes.DWORD()

    res = DeviceIoControl(
        device,
        io_control_code,
        in_buffer,
        in_buffer_size,
        out_buffer,
        out_buffer_size,
        returned_bytes,
        overlapped,
    )

    handle_nonzero_success(res)
    handle_nonzero_success(returned_bytes)

    return out_buffer[: returned_bytes.value]


# Fake the jaraco api
class api:
    CreateFile                   = CreateFile
    CloseHandle                  = CloseHandle
    GetFileInformationByHandle   = GetFileInformationByHandle

    BY_HANDLE_FILE_INFORMATION   = BY_HANDLE_FILE_INFORMATION
    FILE_FLAG_BACKUP_SEMANTICS   = FILE_FLAG_BACKUP_SEMANTICS
    FILE_FLAG_OPEN_REPARSE_POINT = FILE_FLAG_OPEN_REPARSE_POINT
    FILE_SHARE_READ              = FILE_SHARE_READ
    FSCTL_GET_REPARSE_POINT      = FSCTL_GET_REPARSE_POINT
    GENERIC_READ                 = GENERIC_READ
    INVALID_HANDLE_VALUE         = INVALID_HANDLE_VALUE
    IO_REPARSE_TAG_SYMLINK       = IO_REPARSE_TAG_SYMLINK
    OPEN_EXISTING                = OPEN_EXISTING
    REPARSE_DATA_BUFFER          = REPARSE_DATA_BUFFER


class reparse:
    DeviceIoControl = _reparse_DeviceIoControl

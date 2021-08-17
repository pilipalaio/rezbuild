"""Utilities for rez_builder."""

# Import built-in modules
import os
import platform
import re
import shutil
import stat
import struct

# Import local modules
from rezbuild.constants import MACHO_MAGIC_NUMBERS
from rezbuild.exceptions import ArgumentError


def change_shebang(filepath, shebang, is_bin=False, origin_shebang=""):
    """Change shebang of the exe file.

    Args:
        filepath (str): The path of the file you want to change.
        shebang (str): The shebang to change to.
        is_bin (bool): Whether the file is a binary file.
        origin_shebang (str): The original shebang to replaced.
    """
    read_mode, write_mode = "r", "w"
    if is_bin:
        read_mode += "b"
        write_mode += "b"
    if not shebang.startswith("#!"):
        shebang = f"#!{shebang}"
    if origin_shebang and not origin_shebang.startswith("#!"):
        origin_shebang = f"#!{origin_shebang}"

    with open(filepath, read_mode) as file_:
        content = file_.read()

    if origin_shebang and is_bin:
        new_shebang = bytes(shebang, encoding="utf-8")
        origin_shebang = bytes(origin_shebang, encoding="utf-8")
        new_shebang = new_shebang.ljust(len(origin_shebang), b" ")
        new_content = content.replace(origin_shebang, new_shebang)
    elif origin_shebang:
        new_content = content.replace(origin_shebang, shebang)
    else:
        origin_shebang = re.match("#!.+", content).group(0)
        new_content = content.replace(origin_shebang, shebang)

    with open(filepath, write_mode) as file_:
        file_.write(new_content)


def clear_path(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path)


def get_delimiter():
    """Get the system delimiter of the path.

    Returns:
        str: The path delimiter for the system.
    """
    if platform.system() == "Windows":
        return ";"
    else:
        return ":"


def get_lcload_dylibs(macho, ignore_system_dylib=True):
    """Get lcload dylibs from Mach-O file.

    Args:
        macho (str): The Mach-O filepath to get from.
        ignore_system_dylib (bool): Whether to ignore the system dylibs. System
            dylibs means the dylib file under `/usr/lib` or under
            `/System/Library`.

    Returns:
        :obj:`list` of :obj:`str`: The lcload dylibs.
    """
    dylibs = []
    with open(macho, "rb") as file_:
        file_.read(16)
        load_cmd_count = struct.unpack("I", file_.read(4))[0]
        file_.read(12)
        for _ in range(load_cmd_count):
            cmd, size = struct.unpack("2I", file_.read(8))
            if cmd != 12:
                file_.read(size - 8)
                continue
            file_.read(16)
            remain_size = size - 8 - 16
            path = b"".join(struct.unpack(f"{remain_size}c", file_.read(remain_size)))
            path = path.decode("utf-8").strip(b"\x00".decode())
            if not ignore_system_dylib:
                dylibs.append(path)
            elif (not path.startswith("/usr/lib/") and
                  not path.startswith("/System/Library/")):
                dylibs.append(path)
    return dylibs


def get_windows_shebang(filepath, pattern):
    """Get the windows shebang from binary files.

    Args:
        filepath (str): The filepath to get shebang from.
        pattern (str): The re pattern to match shebang.

    Returns:
        str: The matched shebang.
    """
    if not pattern.startswith("#!"):
        pattern = f"#!{pattern}"
    with open(filepath, "rb") as file_:
        content = file_.read()
    match = re.search(bytes(pattern, encoding="utf-8"), content)
    if match:
        return str(match.group(0), encoding="utf-8")
    return ""


def is_macho(filepath):
    """Check if the file is a Mach-O file.

    Args:
        filepath (str): The path of the file to check.

    Returns:
        bool: True if the file is a Mach-O file, false otherwise.
    """
    with open(filepath, "rb") as f:
        magic_number = f.read(4)
    return magic_number in MACHO_MAGIC_NUMBERS


def make_bins_movable(bin_path, shebang, pattern=None):
    """Change all the shebang of entry points to make it movable.

     Args:
         bin_path (str): Where the entry files placed.
         shebang (str): The shebang to change to.
         pattern (str): The re pattern to match shebang.
     """
    for filename in os.listdir(bin_path):
        filepath = os.path.join(bin_path, filename)
        if platform.system() == "Windows":
            if not pattern:
                raise ArgumentError(
                    "Argument `pattern` can not be None on Windows.")
            origin_shebang = get_windows_shebang(filepath, pattern)
            change_shebang(
                filepath, shebang, is_bin=True,
                origin_shebang=origin_shebang)
        else:
            change_shebang(filepath, shebang)


def remove_tree(path):
    """Remove directory.

    Args:
        path (str): The directory to remove.
    """
    def rm_readonly(func, path_, _):
        """Remove read-only files on Windows.

        Reference from https://stackoverflow.com/questions/1889597 and
        https://github.com/ansible/ansible/issues/34335

        Args:
            func (function): Function which will remove the file/folder.
            path_ (str): Path to file/folder which should be removed.
        """
        os.chmod(path_, stat.S_IWRITE)
        func(path_)

    shutil.rmtree(path, onerror=rm_readonly)

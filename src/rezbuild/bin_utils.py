"""This module include some function to make bin movable.

Make windows executable, shell script and Macho-O files movable.
"""

# Import built-in modules
import os
import platform
import re
import shutil
import struct
import subprocess

# Import local modules
from rezbuild.constants import MACHO_MAGIC_NUMBERS
from rezbuild.exceptions import ArgumentError
from rezbuild.utils import get_relative_path


def add_rpath(macho, rpath):
    """Add rpath into Macho-O file.

    Only work in macOS.

    Args:
        macho (str): The path of the macho file to add rpath.
        rpath (str): The rpath to add.
    """
    cmd = ["install_name_tool", "-add_rpath", rpath, macho]
    subprocess.run(cmd, check=True)


def change_lcload(filepath, old_path, new_path):
    """Change the lcload path.

    Only work in macOS.

    Args:
        filepath (str): The path of the file to change.
        old_path (str): The old lcload path to change.
        new_path (str): The new lcload path to change to.
    """
    cmd = ["install_name_tool", "-change", old_path, new_path, filepath]
    subprocess.run(cmd, check=True)


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
            path = b"".join(struct.unpack(f"{remain_size}c",
                                          file_.read(remain_size)))
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


def make_bins_movable(bin_path, shebang="", pattern="", rpath="", lib_dir=""):
    """Change all the bins in the directory to make it movable.

    Args:
        bin_path (str): Where the entry files placed.
        shebang (str, optional): The shebang to change to.
        pattern (str, optional): The re pattern to match shebang.
        rpath (str, optional): The rpath to add.
        lib_dir (str, optional): The destination path to put the dylib file to.
    """
    for filename in os.listdir(bin_path):
        filepath = os.path.join(bin_path, filename)
        if platform.system() == "Windows":
            if not pattern:
                raise ArgumentError(
                    "Argument `pattern` can not empty on Windows.")
            if not shebang:
                raise ArgumentError(
                    "Argument `shebang` can not empty on Windows.")
            origin_shebang = get_windows_shebang(filepath, pattern)
            change_shebang(
                filepath, shebang, is_bin=True, origin_shebang=origin_shebang)
        else:
            if is_macho(filepath):
                make_macho_movable(filepath, rpath, lib_dir)
            else:
                change_shebang(filepath, shebang)


def make_macho_movable(macho_path, rpath="", lib_dir=""):
    """Make the macho file movable.

    Copy the unmovable dylibs into the dst_dir and add the rpath into macho.

    Args:
        macho_path (str): The macho file path to modify.
        rpath (str, optional): The rpath to add. Default is the relative path
            between the macho_path and dst_dir.
        lib_dir (str, optional): The destination path to put the dylib file to.
            Default is the "lib" folder in the same level directory as the
            parent directory of macho_path.
    """

    lib_dir = lib_dir or os.path.join(
        os.path.dirname(os.path.dirname(macho_path)), "lib")
    rpath = rpath or os.path.join(
        "@executable_path",
        get_relative_path(os.path.dirname(macho_path), lib_dir))
    add_rpath(macho_path, rpath)

    def copy_and_change(macho):
        """Copy dylibs and change lcload path.

        Args:
            macho (str): The macho file to change.
        """
        dylibs = get_lcload_dylibs(macho)
        for dylib in dylibs:
            lib_name = os.path.basename(dylib)
            change_lcload(macho, dylib, f"@rpath/{lib_name}")
            if lib_name not in os.listdir(lib_dir):
                dst = os.path.join(lib_dir, lib_name)
                shutil.copy2(dylib, dst)
                copy_and_change(dylib)

    copy_and_change(macho_path)

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
from rezbuild.exceptions import ArgumentError
from rezbuild.utils import get_relative_path


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


def make_bins_movable(
        bin_path, shebang="", pattern="", rpath="", lib_dir="",
        change_load_dylib=True):
    """Change all the bins in the directory to make it movable.

    Args:
        bin_path (str): Where the entry files placed.
        shebang (str, optional): The shebang to change to. Default is `""`.
        pattern (str, optional): The re pattern to match shebang. Default is
            `""`.
        rpath (str, optional): The rpath to add. Default is `""`.
        lib_dir (str, optional): The destination path to put the dylib file to.
            Default is `""`.
        change_load_dylib (str, optional): Whether to change the load dylib
            path to rpath. Default is True.
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
            if MachO.is_macho(filepath):
                MachO(filepath).make_macho_movable(
                    rpath, lib_dir, change_load_dylib)
            else:
                change_shebang(filepath, shebang)


class MachO(object):

    # Mach-O files will contain on of the follow magic numbers at the beginning
    # of the file.
    LOAD_COMMANDS_MAPPING = {
        12: "parse_load_dylib",
        2147483676: "parse_rpath",
    }

    # The magic numbers of Mach-O files
    MACHO_MAGIC_NUMBERS = [
        b"\xcf\xfa\xed\xfe",
        b"\xce\xfa\xed\xfe",
        b"\xca\xfe\xba\xbe",
    ]

    # File path prefix of the system dylib.
    SYSTEM_DYLIB_PREFIX = [
        "/usr/lib/",
        "/System/Library/",
    ]

    def __init__(self, path):
        """Initialize.

        Args:
            path (str): The path of the Mach-O file.
        """
        self.load_dylibs = []
        self.path = path
        self.rpaths = []
        self.parse_load_command()

    def add_rpath(self, rpath):
        """Add rpath into Macho-O file.

        Args:
            rpath (str): The rpath to add.
        """
        cmd = ["install_name_tool", "-add_rpath", rpath, self.path]
        subprocess.run(cmd, check=True)

    def change_load_dylib(self, old_path, new_path):
        """Change the load dylib path.

        Args:
            old_path (str): The old load dylib to change.
            new_path (str): The new load dylib to change to.
        """
        cmd = ["install_name_tool", "-change", old_path, new_path, self.path]
        subprocess.run(cmd, check=True)

    @staticmethod
    def decode_str(content):
        """Decode bytes to str.

        Args:
            content (bytes): The bytes to decode.
        """
        result = b"".join(struct.unpack(f"{len(content)}c", content))
        return result.decode("utf-8").strip(b"\x00".decode())

    def get_default_libdir(self):
        """Get the path of the lib dir under the package root.

        Assume the package tree like this:
        package_root/
            |___bin/
                |___Mach-O file
            |___include/
            |___lib/
                |___lib1
                |___lib2
            |___share/
        """
        return os.path.join(
            os.path.dirname(os.path.dirname(self.path)), "lib")

    def get_default_rpath(self, libdir=None):
        """Get the the rpath relative with the lib path.

        Args:
            libdir (str, optional): The lib dir to calculate the rpath. Default
                is the lib dir under the package root.
        """
        libdir = libdir or self.get_default_libdir()
        return os.path.join(
            "@executable_path",
            get_relative_path(os.path.dirname(self.path), libdir))

    def get_load_dylibs(self, ignore_system_dylib=False):
        """Get all the dylibs in this Mach-O files.

        Args:
            ignore_system_dylib (bool, optional): Whether include the system
                dylibs. Default is False.
        """
        if ignore_system_dylib:
            return self.get_non_system_dylibs()
        else:
            return self.load_dylibs

    def get_non_system_dylibs(self):
        """Get dylibs that doesn't contain system dylibs."""
        non_system_dylibs = []
        for dylib in self.load_dylibs:
            for prefix in self.SYSTEM_DYLIB_PREFIX:
                if dylib.startswith(prefix):
                    break
            else:
                non_system_dylibs.append(dylib)
        return non_system_dylibs

    @classmethod
    def is_macho(cls, filepath):
        """Check if the file is a Mach-O file.

        Args:
            filepath (str): The path of the file to check.

        Returns:
            bool: True if the file is a Mach-O file, false otherwise.
        """
        with open(filepath, "rb") as f:
            magic_number = f.read(4)
        return magic_number in cls.MACHO_MAGIC_NUMBERS

    def make_macho_movable(self, rpath="", lib_dir="", change_load_dylib=True):
        """Make the macho file movable.

        Copy the unmovable dylibs into the dst_dir and add the rpath into
        macho.

        Args:
            rpath (str, optional): The rpath to add. Default is the relative
                path between the macho_path and dst_dir.
            lib_dir (str, optional): The destination path to put the dylib file
                to. Default is the "lib" folder in the same level directory as
                the parent directory of macho_path.
            change_load_dylib (bool, optional): Whether to change the load
                dylib path to rpath. Default is True.
        """
        lib_dir = lib_dir or self.get_default_libdir()
        rpath = rpath or self.get_default_rpath(lib_dir)
        if change_load_dylib and rpath not in self.rpaths:
            self.add_rpath(rpath)

        def copy_and_change(macho):
            """Copy dylibs and change lcload path.

            Args:
                macho (MachO): The macho object to change.
            """
            for dylib in macho.get_load_dylibs(ignore_system_dylib=True):
                lib_name = os.path.basename(dylib)
                if change_load_dylib:
                    macho.change_load_dylib(dylib, f"@rpath/{lib_name}")
                if lib_name not in os.listdir(lib_dir):
                    dst = os.path.join(lib_dir, lib_name)
                    shutil.copy2(dylib, dst)
                    copy_and_change(MachO(dylib))

        copy_and_change(self)

    def parse_load_command(self):
        """Parse Mach-O file load commands."""
        with open(self.path, "rb") as file_:
            file_.read(16)
            load_cmd_count = struct.unpack("I", file_.read(4))[0]
            file_.read(12)
            for _ in range(load_cmd_count):
                cmd, size = struct.unpack("2I", file_.read(8))
                content = file_.read(size - 8)
                if cmd not in self.LOAD_COMMANDS_MAPPING.keys():
                    continue
                func = self.LOAD_COMMANDS_MAPPING[cmd]
                getattr(self, func)(content)

    def parse_rpath(self, content):
        """Parse rpath from the given rpath content.

        Args:
            content (bytes): Part of the Mach-O file content that contain the
                rpath to parse.
        """
        self.rpaths.append(self.decode_str(content[4:]))

    def parse_load_dylib(self, content):
        """Parse load dylib from the given content.

        Args:
            content (bytes): Part of the Mach-O file content that contain the
                load dylib to parse.
        """
        self.load_dylibs.append(self.decode_str(content[16:]))

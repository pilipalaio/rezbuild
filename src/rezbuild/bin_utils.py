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
from rezbuild.exceptions import ReNotMatchError
from rezbuild.utils import get_relative_path


def change_shebang(filepath, shebang, is_bin=False, origin_shebang=""):
    """Change shebang of the exe file.

    Args:
        filepath (str): The path of the file you want to change.
        shebang (str): The shebang to change to.
        is_bin (bool): Whether the file is a binary file.
        origin_shebang (str): The original shebang to replaced.
    """
    if not shebang.startswith("#!"):
        shebang = f"#!{shebang}"
    if origin_shebang and not origin_shebang.startswith("#!"):
        origin_shebang = f"#!{origin_shebang}"

    read_mode, write_mode = "r", "w"
    if is_bin:
        read_mode += "b"
        write_mode += "b"
        shebang = bytes(shebang, encoding="utf-8")

    with open(filepath, read_mode) as file:
        content = file.read()

    if origin_shebang and is_bin:
        origin_shebang = bytes(origin_shebang, encoding="utf-8")
        shebang = shebang.ljust(len(origin_shebang), b" ")
    elif origin_shebang:
        pass
    elif is_bin:
        match = re.match(b"#!.+", content)
        if match:
            origin_shebang = match.group(0)
        else:
            raise ReNotMatchError(f"Can't find shebang in file `{filepath}`")
    else:
        match = re.match("#!.+", content)
        if match:
            origin_shebang = match.group(0)
        else:
            raise ReNotMatchError(f"Can't find shebang in file `{filepath}`")

    with open(filepath, write_mode) as file:
        file.write(content.replace(origin_shebang, shebang))


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
    with open(filepath, "rb") as file:
        content = file.read()
    match = re.search(bytes(pattern, encoding="utf-8"), content)
    if match:
        return str(match.group(0), encoding="utf-8")
    return ""


def make_bin_movable(
        bin_path, shebang="", pattern="", lib_dir="", extra_lib_dirs=None,
        add_rpath=True):
    """Make bin file movable.

    Args:
        bin_path (str): Path of the bin file.
        shebang (str, optional): The shebang to change to. Default is "".
        pattern (str, optional): The re pattern to match shebang. Default is
            `""`.
        lib_dir (str, optional): The destination path to put the dylib file to.
            Default is `""`.
        extra_lib_dirs (:obj:`list` of :obj:`str`, optional): The extra library
            directory to check if the dylib file should be copied. The dylib
            file will not be copied when it in the exclude_lib_dirs.
        add_rpath (bool, optional): Whether to add rpath into macho. Default is
            True.
    """
    if platform.system() == "Windows":
        if not pattern:
            raise ArgumentError(
                "Argument `pattern` can not empty on Windows.")
        origin_shebang = get_windows_shebang(bin_path, pattern)
        change_shebang(
            bin_path, shebang, is_bin=True, origin_shebang=origin_shebang)
    else:
        if MachO.is_macho(bin_path):
            macho = MachO(bin_path)
            if not macho.static:
                macho.make_macho_movable(lib_dir, extra_lib_dirs, add_rpath)
        else:
            change_shebang(bin_path, shebang)


def make_bins_movable(
        path, shebang="", pattern="", lib_dir="", extra_lib_dirs=None,
        add_rpath=True):
    """Make all the bins movable which in the directory.

    Args:
        path (str): Path to the directory.
        shebang (str, optional): The shebang to change to. Default is "".
        pattern (str, optional): The re pattern to match shebang. Default is
            `""`.
        lib_dir (str, optional): The destination path to put the dylib file to.
            Default is `""`.
        extra_lib_dirs (:obj:`list` of :obj:`str`, optional): The extra library
            directory to check if the dylib file should be copied. The dylib
            file will not be copied when it in the exclude_lib_dirs.
        add_rpath (bool, optional): Whether to add rpath into macho. Default is
            True.
    """
    for filename in os.listdir(path):
        filepath = os.path.join(path, filename)
        if os.path.isdir(filepath) or os.path.islink(filepath):
            continue
        make_bin_movable(
            filepath, shebang, pattern, lib_dir, extra_lib_dirs, add_rpath)


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
        self.fat = False
        self.load_dylibs = []
        self.macho = False
        self.path = path
        self.rpaths = []
        self.static = False
        self._parse_file()

    def _parse_file(self):
        """Parse the MachO file."""
        with open(self.path, "rb") as file:
            magic_number = file.read(4)
            if magic_number in self.MACHO_MAGIC_NUMBERS:
                self.macho = True
            else:
                return
            if magic_number == b"\xca\xfe\xba\xbe":
                self.fat = True
                arch_count = struct.unpack(">I", file.read(4))[0]
                # Each fat header has 5 entity. Each entity occupies 4 bytes.
                offsets = self.get_fat_offsets(
                    arch_count, file.read(20 * arch_count))
                content = b"\x00" * (8 + arch_count * 20) + file.read()
            else:
                offsets = [0]
                content = magic_number + file.read()
        self.parse_arch(content, offsets)

    def add_rpath(self, rpath):
        """Add rpath into Macho-O file.

        Args:
            rpath (str): The rpath to add.
        """
        cmd = ["install_name_tool", "-add_rpath", rpath, self.path]
        subprocess.run(cmd, check=True)

    def change_dylib_id(self, dylib_id):
        """change the load dylib ID.

        Args:
            dylib_id (str): The id to change to.
        """
        cmd = ["install_name_tool", "-id", dylib_id, self.path]
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

    @staticmethod
    def get_fat_offsets(arch_count, content):
        """Get the offsets from the MachO universal binary file.

        Args:
            arch_count (int): The architecture number of the MachO file.
            content (bytes): The header content of the fat file.
        """
        offsets = []
        for i in range(arch_count):
            offset = struct.unpack(">I", content[i * 20 + 8:i * 20 + 12])[0]
            offsets.append(offset)
        return offsets

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

    @staticmethod
    def get_magic_number(filepath):
        """Get magic number from file.

        Args:
            filepath (str): The file to get magic number from.
        """
        with open(filepath, "rb") as f:
            return f.read(4)

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
        return cls.get_magic_number(filepath) in cls.MACHO_MAGIC_NUMBERS

    def make_macho_movable(
            self, lib_dir="", extra_lib_dirs=None, add_rpath=True):
        """Make the macho file movable.

        Args:
            lib_dir (str, optional): The destination path to put the dylib file
                to. Default is the "lib" folder in the same level directory as
                the parent directory of macho_path.
            extra_lib_dirs (:obj:`list` of :obj:`str`, optional): The extra
                library directory to add to rpath. The dylib files will not be
                copied when it already in extra_lib_dirs.
            add_rpath (bool, optional): Whether to add rpath into macho.
                Default is True.
        """
        lib_dir = lib_dir or self.get_default_libdir()
        extra_lib_dirs = extra_lib_dirs or []
        extra_lib_dirs.append(lib_dir)
        if add_rpath:
            for dir_ in extra_lib_dirs:
                rpath = self.get_default_rpath(dir_)
                if rpath not in self.rpaths:
                    self.add_rpath(rpath)
                    self.rpaths.append(rpath)

        def copy_and_change(macho):
            """Copy dylibs and change lcload path.

            Args:
                macho (MachO): The macho object to change.
            """
            macho.change_dylib_id(f"@rpath/{os.path.basename(macho.path)}")
            for dylib in macho.get_load_dylibs(ignore_system_dylib=True):
                lib_name = os.path.basename(dylib)
                macho.change_load_dylib(dylib, f"@rpath/{lib_name}")
                for extra_lib_dir in extra_lib_dirs:
                    if lib_name in os.listdir(extra_lib_dir):
                        copy_and_change(
                            MachO(os.path.join(extra_lib_dir, lib_name)))
                        break
                else:
                    dst = os.path.join(lib_dir, lib_name)
                    shutil.copy2(dylib, dst)
                    copy_and_change(MachO(dst))

        copy_and_change(self)

    def parse_arch(self, content, offsets):
        """Parse the MachO file architecture.

        Args:
            content (bytes): The MachO file content.
            offsets (:obj:`list` of :obj:`int`): The offset of each
                architecture in MachO file.
        """
        for offset in offsets:
            magic_number = content[offset:offset + 4]
            if magic_number not in self.MACHO_MAGIC_NUMBERS:
                self.static = True
                break
            load_cmd_count = struct.unpack(
                "I", content[offset + 16:offset + 20])[0]
            feed = 32 + offset
            for _ in range(load_cmd_count):
                cmd, size = struct.unpack("2I", content[feed:feed + 8])
                if cmd not in self.LOAD_COMMANDS_MAPPING.keys():
                    feed += size
                    continue
                func = self.LOAD_COMMANDS_MAPPING[cmd]
                getattr(self, func)(content[feed + 8:feed + size])
                feed += size

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

"""Utilities for rez_builder."""

# Import built-in modules
import os
import platform
import re
import shutil
import stat

# Import local modules
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

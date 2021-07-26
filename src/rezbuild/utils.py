"""Utilities for rez_builder."""

# Import built-in modules
import os
import platform
import re
import shutil
import stat


def change_shabang(filepath, shabang, is_bin=False, origin_shabang=""):
    """Change shabang of the exe file.

    Args:
        filepath (str): The path of the file you want to change.
        shabang (str): The shabang you want to change to. Do not include `#!`.
        is_bin (bool): If the file is a binary file.
        origin_shabang (str): The original shabang to replaced. Do not include
            `#!`.
    """
    read_mode, write_mode = "r", "w"
    if is_bin:
        read_mode += "b"
        write_mode += "b"

    with open(filepath, read_mode) as file_:
        if origin_shabang and is_bin:
            origin_shabang = f"#!{origin_shabang}"
            new_shabang = bytes(f"#!{shabang}", encoding="utf-8")
            new_shabang = new_shabang.ljust(len(origin_shabang), b" ")
            new_content = file_.read().replace(origin_shabang, new_shabang)
        elif origin_shabang:
            origin_shabang = f"#!{origin_shabang}"
            new_content = file_.read().replace(origin_shabang, f"#!{shabang}")
        else:
            content = file_.read()
            origin_shabang = re.match(r"#!.+", content).group(0)
            new_content = content.replace(origin_shabang, f"#!{shabang}")

    with open(filepath, write_mode) as file_:
        file_.write(new_content)


def get_delimiter():
    """Get the system delimiter of the path.

    Returns:
        str: The path delimiter for the system.
    """
    if platform.system() == "Windows":
        return ";"
    else:
        return ":"


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

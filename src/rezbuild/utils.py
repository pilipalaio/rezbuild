"""Utilities for rez_builder."""

# Import built-in modules
import os
import platform
import shutil
import stat

# Import local modules
from rezbuild.exceptions import FileAlreadyExistError


def clear_path(path):
    """Remove all the files and directories under the path.

    Args:
        path (str): The path to clear.
    """
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path)


def copy_tree(
        src, dst, dirs_exist_ok=False, follow_symlinks=True,
        file_overwrite=False):
    """

    """
    if not dirs_exist_ok or not os.path.exists(dst):
        shutil.copytree(src, dst, symlinks=follow_symlinks)
    else:
        for file in os.listdir(src):
            src_ = os.path.join(src, file)
            dst_ = os.path.join(dst, file)
            if os.path.isfile(src_) or os.path.islink(src_):
                if not os.path.exists(dst_):
                    shutil.copy2(src_, dst_)
                elif os.path.exists(dst_) and file_overwrite:
                    shutil.copy2(src_, dst_)
                else:
                    raise FileAlreadyExistError(
                        f"File {dst_} already exist. Set the file_overwrite "
                        f"as True if you want overwrite it.")
            else:
                copy_tree(
                    src_, dst_, dirs_exist_ok=dirs_exist_ok,
                    follow_symlinks=follow_symlinks,
                    file_overwrite=file_overwrite)


def get_delimiter():
    """Get the system delimiter of the path.

    Returns:
        str: The path delimiter for the system.
    """
    if platform.system() == "Windows":
        return ";"
    else:
        return ":"


def get_relative_path(from_path, to_path):
    """Get the relative path between two paths.

    Args:
        from_path (str): The path where the relative path from.
        to_path (str): The path where the relative path to.
    """
    from_path = from_path.replace("\\", "/")
    to_path = to_path.replace("\\", "/")
    folders1, folders2 = from_path.split("/"), to_path.split("/")
    length = min(len(folders1), len(folders2))
    for i in range(length):
        folder1, folder2 = folders1[i], folders2[i]
        if folder1 != folder2:
            length = i
            break
    return "/".join(['..'] * (len(folders1) - length) + folders2[length:])


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

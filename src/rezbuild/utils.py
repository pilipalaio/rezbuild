"""Utilities for rez_builder."""

# Import built-in modules
import os
import platform
import shutil
import stat


def clear_path(path):
    """Remove all the files and directories under the path.

    Args:
        path (str): The path to clear.
    """
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


def get_relative_path(from_path, to_path):
    """Get the relative path between two paths.

    Args:
        from_path (str): The path where the relative path from.
        to_path (str): The path where the relative path to.
    """
    from_path = from_path.replace("\\", "/")
    to_path = to_path.replace("\\", "/")
    folders1, folders2 = from_path.split("/"), to_path.split("/")
    for i in range(min(len(folders1), len(folders2))):
        folder1, folder2 = folders1[i], folders2[i]
        if folder1 != folder2:
            return "/".join(['..'] * (len(folders1) - i) + folders2[i:])
    return ""


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

"""Utilities for rez_builder."""

# Import built-in modules
import os
import shutil
import stat


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

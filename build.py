#!/usr/bin/env python

"""Build this package by self.

This file is only for rez to build the package.
"""

# Import build-in modules
import os
import sys

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

# Import third-party modules
from rezbuild.builder import PythonSourceBuilder


if __name__ == '__main__':
    PythonSourceBuilder().build(is_venv=False)

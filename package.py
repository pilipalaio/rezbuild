# -*- coding: utf-8 -*-

name = "rezbuild"

version = "0.12.0"

tools = []

variants = []

requires = [
    "build-0.3+",
    "pip-18+",
    "python-3.6+<4",
]

private_build_requires = [
    "setuptools-42+",
    "wheel",
]

build_command = "python {root}/build.py {install}"


def commands():
    env.PYTHONPATH.append("{root}/site-packages")

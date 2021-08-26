# -*- coding: utf-8 -*-

name = "rezbuild"

tools = []

variants = []

requires = [
    "build-0.3+",
    "pip-18+",
    "python-3.8+",
]

private_build_requires = [
    "git",
    "setuptools-42+",
    "setuptools_scm-3.4+",
    "wheel",
]

build_command = "python {root}/build.py {install}"


def commands():
    env.PYTHONPATH.append("{root}/site-packages")


@early()
def version():
    import os
    import platform
    import sys
    from rez.resolved_context import ResolvedContext
    context = ResolvedContext(["setuptools_scm", "git"])
    if platform.system() == "Windows":
        delimiter = ";"
    else:
        delimiter = ":"
    paths = context.get_environ()["PATH"].split(delimiter)
    pythonpaths = context.get_environ()["PYTHONPATH"].split(delimiter)
    os.environ["PATH"] = delimiter.join(paths)
    sys.path.extend(pythonpaths)
    from setuptools_scm import get_version
    return get_version()

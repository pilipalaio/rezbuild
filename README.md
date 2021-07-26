# Rezbuild

Rezbuild is a python library for build rez packages. Please visit the 
[Rez website](https://github.com/nerdvegas/rez) for more information about rez.

点击 [这里](https://gitlab.com/Pili-Pala/rezbuild/-/blob/main/README_zh_CN.md)
访问 Rezbuild 的中文文档。

## Description

### Goal

This project is a build tool to build rez packages. We always need to do some
of the same steps when we build a rez package. Just like extract zip file,
install the wheel file using pip, copy files to the installation directory. The
goal of this project is to cover all the repetitive work when building rez
package.

## Getting Started

### requisites

Rezbuild requires the python-3.6+, build-0.3+(lower version did not test) and
pip-18+ to run. If you want to install this package from source, git and
setuptools_scm are also needed.

### Installing

1.Install by rezbuild

The recommended way to install this package is using itself. Make sure you have
all the requirements are installed into rez environment, include rezbuild(early
version of this package).
Download wheel file from [PyPI](https://pypi.org/project/rezbuild/#files)
And then create a directory like this:

```text
install_rezbuild/
    |___rez_installers/
        |___0/
            |___rezbuild-0.1.1-py3-none-any.whl
    |___build.py
    |___package.py
```
The content of build.py can be like this:

```python
# build.py
from rezbuild.builder import PythonWheelBuilder


if __name__ == '__main__':
    builder = PythonWheelBuilder()
    builder.build()
```

The content of package.py can be like this:
```python
# package.py
name = "rezbuild"

version = "version of this package you download"

requires = [
    "build-0.3+",
    "pip-18+",
    "python-3.6+",
]

private_build_requires = [
    "rezbuild",
]

build_command = 'python {root}/build.py {install}'


def commands():
    env.PYTHONPATH.append("{root}/site-packages")
```

Then, run this command in the root directory
`rez build -i`

After that, this package will be installed as a rez package.

2.Install by source for rez

If you are new in rezbuild, or there's no early rezbuild version in you rez
environment, you can use rez to install this package from source. Make sure all
the requirement already installed into you rez environment(python-3.6+,
build-0.3+, pip-18+, [git, setuptools_scm]). If you do not have setuptools_scm
in you rez environment, please change the `version` argument to the version of
rezbuild you download in `package.py` file . The default way to get the version
number is using setuptools_scm to auto get it.

Then, clone this project, cd the source root and run the rez install command:

```shell
git clone git@gitlab.com:Pili-Pala/rezbuild.git
cd rezbuild
rez build -i
```

3.Install from pypi

Of course, you can install this package from pip

```shell
pip install rezbuild
```

As this package is for rez, install from pypi doesn't make sense in most of the
time.

## Running the tests

### Break down into end-to-end tests

WIP

### Coding style tests

WIP

## Usage

After 2.70.0, rez removed the bez build system. So the docs is based on 
rez-2.70.0.

Rezbuild support different build types, like build from whl file, build from
source, or you can customize you build function.

### Build from python wheel file

I assume that you already know what is rez, how to make a package.py, and now
you want to build a python package come from the internet.

Fist, add a build file into you package root, just like a file named
`build.py`. The content can be like this:

```python
# Import third-party modules
from rezbuild import PythonWheelBuilder


if __name__ == '__main__':
    PythonWheelBuilder().build()
```

Then add the attribute build_command into the `package.py` file,
content should be like this: 
`build_command = 'python {root}/build.py {install}'`.

After that, go to [PyPI](https://pypi.org) to download the wheel file and put
the file into `source_root/rez_installers/0`. The tree should like this:

```text
source_root/
    |___rez_installers/
        |___0/
            |___the_package_you_want_to_install.whl
    |___build.py
    |___package.py
```

Finally, run the command `rez build -i`, the package will be installed.

### Build from python source code

The only different between build from wheel file is the builder. Change the
content of `build.py` like this:

```python
# Import third-party modules
from rezbuild import PythonSourceBuilder


if __name__ == '__main__':
    PythonSourceBuilder().build()
```

Then ensure you already make all the necessary files to build a python package.
Check with this 
[tutorial](https://packaging.python.org/tutorials/packaging-projects/).

Then run the command `rez build -i`, the package will be build and installed.

### Custom builder

You can customize a builder for you code from base builder. 

#### RezBuilder
`RezBuilder` is the root builder, all the builder inherit from it. It gets the
rez environment, make sure the workspace, install package, and customize you
own build function.

For example:
```python
# Import built-in modules
import os
import shutil

# Import third-party modules
from rezbuild import RezBuilder


class CustomBuilder(RezBuilder):

    def custom_build(self):
        shutil.copytree(os.path.join(self.source_path, "src"), self.build_path)


if __name__ == '__main__':
    CustomBuilder().build()
```

build function will invoke the custom_build function to build the package.


## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available,
see the [tags on this repository](https://gitlab.com/Pili-Pala/rezbuild/tags).

## Author
[PiliPala](https://gitlab.com/Pili-Pala)

## License
[GPLv3](https://www.gnu.org/licenses/gpl-3.0.txt)

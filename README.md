# Rezbuild

Rezbuild is a python library for build rez packages. Please visit the 
[Rez website](https://github.com/nerdvegas/rez) for more information about rez.

点击 [这里](https://gitlab.com/Pili-Pala/rezbuild/-/blob/main/README_zh_CN.md)
访问 Rezbuild 的中文文档。

## Description

This project is a tool to build rez packages. It simplifies the build process.

Rezbuild support build rez package by python wheel, python source archive,
python source, archive file, unix source, macOS pkg and macOS dmg.

## Installation

### requisites

Rezbuild requires the python-3.6+, build-0.3+(lower version did not test) and
pip-18+ to run.

### Install

There are 3 ways to install rezbuild, choose according to your own situation.

#### 1.Install by source for rez(New in rezbuild, or do not have rezbuild in you environment)

If you are new in rezbuild, or there's no other version of rezbuild in you rez
environment, you can use rez to install this package from source. Make sure all
the requirement already installed into you rez environment(python-3.6+,
build-0.3+, pip-18+).

Then, clone this project, cd the source root and run the rez install command:

```shell
git clone git@gitlab.com:Pili-Pala/rezbuild.git
cd rezbuild
rez build -i
```

#### 2.Install by itself(Need rezbuild in you rez repository)

Rezbuild can install by itself. Make sure you have all the requirements are
installed into rez environment, include rezbuild (another version of this
package). Download wheel file from
[PyPI](https://pypi.org/project/rezbuild/#files). Then create a directory like
this:

```text
install_rezbuild/
├── build.py
├── package.py
└── installers/
    └── rezbuild-0.14.1-py3-none-any.whl

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

Then, run this command in the root directory `rez build -i`.
After that, this package will be installed as a rez package.

#### 3.Install from pypi

Of course, you can install this package from pip

```shell
pip install rezbuild
```

As this package is for rez, install from pypi doesn't make sense in most of the
time.

## Usage

After 2.70.0, rez removed the bez build system. So rezbuild based on
rez-2.70.0.

### Build from python wheel file(PythonWheelBuilder)

I assume that you already know what is rez, how to make a package.py, and now
you want to build a third-party python package come from the internet.

First, add a build file into you package root, just like a file named
`build.py`. The content can be like this:

```python
# Import third-party modules
from rezbuild import PythonWheelBuilder


if __name__ == '__main__':
    PythonWheelBuilder().build()
```

Then add variable `build_command` into the `package.py` file,
content should be like this: 
`build_command = 'python {root}/build.py {install}'`.

After that, go to [PyPI](https://pypi.org) to download the wheel file and put
the file into `source_root/installers`. The tree should like this:

```text
source_root/
├── build.py
├── package.py
└── installers/
    └── the_package_you_want_to_install.whl
```

Finally, change directory to source_root and run the command `rez build -i`,
the package will be installed.

### Build from python source code(PythonSourceBuilder)

PythonSourceBuilder is used to build rez package from python source which
meeting the requirements of Python official structure. The source structure
please refer to
[python official website](https://packaging.python.org/en/latest/tutorials/packaging-projects/).
The source structure should like this:

```text
source_root/
├── build.py
├── package.py
├── pyproject.toml
├── setup.cfg
└── src/
    └── module/
        └── __init__.py

```

The content of `build.py`:

```python
# Import third-party modules
from rezbuild import PythonSourceBuilder


if __name__ == '__main__':
    PythonSourceBuilder().build()

```

Then ensure you already make all the necessary files to build a python package.
`PythonSourceBuilder` will use the official way to build the package.

Then run the command `rez build -i`, the package will be build and installed.

### Build from the python source archive file

Some packages only supply the python source archive file, we can use the
PythonSourceArchiveBuilder builder to build.

### Copy build(CopyBuilder)

Sometimes we don't want to use the official way to build rez package(metadata
will be missing if we don't use the official way), but only copy the code. Use
CopyBuilder can build package by only copy the source code. The default source
path is the folder named `src` under the source root. Pass the path to the root
parameter in build method to custom the source path. build.py file should like
this:

```python
# Import built-in modules
import os

# Import third-party modules
from rezbuild import CopyBuilder


if __name__ == '__main__':
    builder = CopyBuilder()
    builder.build(root=os.path.join(builder.source_path, "example_package"))

```

### Build from Archive file(ExtractBuilder)

ExtractBuilder can extract the archive file to build rez package.
ExtractBuilder now support zip, tar.gz, tar.xz and 7z.exe.

`build.py`:

```python
# Import third-party modules
from rezbuild import ExtractBuilder


if __name__ == '__main__':
    ExtractBuilder().build()

```

Put the archive file into `installers` folder.

```text
source_root/
├── build.py
├── package.py
└── installers/
    └── archive.zip

```

### Build from source code(CompileBuilder)

CompileBuilder support use `configure` and `make` command to build package
on Linux and macOS. The arguments of configure is passed by the
extra_config_args parameter of CompileBuilder.build method.

`build.py` 如下:

```python
# Import third-party modules
from rezbuild import CompileBuilder


if __name__ == '__main__':
    CompileBuilder().build(extra_config_args=["LDFLAGS=-L/path/to/lib"])

```

Put the source archive file into installers folder.

```text
source_root/
├── build.py
├── package.py
└── installers/
    └── git-2.32.0.tar.gz

```

### Build from dmg file(MacOSDmgBuilder)

Make `build.py` like this:

```python
# Import third-party modules
from rezbuild import MacOSDmgBuilder


if __name__ == '__main__':
    MacOSDmgBuilder().build()
```

Put archive file into `installers` folder.

```text
source_root/
├── build.py
├── package.py
└── installers/
    └── installer.dmg
```

Then run command `rez build -i` from `source_root`.

`MacOSDmgBuilder` will create a shell script in the package root, has a same
with the `.app` folder. Set `create_shell` to `False` to prevent his creation.
For example: `MacOSDmgBuilder().build(create_shell=False)`

### Custom builder

You can customize a builder for you code from base builder. Just make a builder
inherit from RezBuilder and rewrite `custom_build` function. Follow will
introduce all the default builder from rezbuild so that you can use them to
customize you own builder.

#### RezBuilder
`RezBuilder` is the root builder, all the builder inherit from it. It gets the
rez environment, make sure the workspace, install package, and execute you
custom build function.

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

### Multiple variant
If you need to install a multi-variant package with different installers for
each variant, you can put the installers into the folders that named with the
variant index under the `installers` folder. For example:

```text
git/
    |___installers/
        |___0
            |___PortableGit-2.32.0.2-64-bit.7z.exe
        |___1
            |___git-2.32.0.tar.xz
    |___build.py
    |___package.py
```

Rezbuild will get all the installers under the variant folder when building it.

## API

### builder module

### RezBuilder()

`RezBuilder` is the root builder, any other builder is inherited from it. 
RezBuilder load the environment variables, makesure the workspace, install the
package and execute the custom build method.

### RezBuilder.build_path

Build path. The rez default directory.

### RezBuilder.install_path

Install path. Default is ~/packages.

### RezBuilder.source_path

The source path.

### RezBuilder.workspace

Workspace. All the files and folders will be copied to the installation path.

### RezBuilder.name

Package name.

### RezBuilder.version

Build version.

### RezBuilder.variant_index

Variant index.

### RezBuilder.build(**kwargs) -> None

Build method, trigger the build process. This method will invoke the custom
build method of the subclass to run the build.

kwargs: Accept all the key word arguments to pass to the custom_build method.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available,
see the [tags on this repository](https://gitlab.com/Pili-Pala/rezbuild/tags).

## Author
[PiliPala](https://gitlab.com/Pili-Pala)

## License
[GPLv3](https://www.gnu.org/licenses/gpl-3.0.txt)

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
├── build.py
├── package.py
└── installers/
    ├── 0
    │   └── PortableGit-2.32.0.2-64-bit.7z.exe
    └── 1
        └── git-2.32.0.tar.xz

```

Rezbuild will get all the installers under the variant folder when building it.

## API

### builder module

### RezBuilder()

`RezBuilder` is the root builder, any other builder is inherited from it. 
RezBuilder load the environment variables, make sure the workspace, install the
package and execute the custom build method.

### RezBuilder.build_path

str: Build path. The rez default directory.

### RezBuilder.install_path

str: Install path. Default is ~/packages.

### RezBuilder.source_path

str: The source path.

### RezBuilder.workspace

str: Workspace. All the files and folders will be copied to the installation
path.

### RezBuilder.name

str: Package name.

### RezBuilder.version

str: Build version.

### RezBuilder.variant_index

str: Variant index.

### RezBuilder.build(**kwargs) -> None

Build method, trigger the build process. This method will invoke the custom
build method of the subclass to run the build.

kwargs: Accept all the key word arguments to pass to the custom_build method.

### CopyBuilder() -> None

Copy all the files into the installation directory(`this.root`).

### CopyBuilder.build(root="") -> None

root(str): All the files under this root will be copied into installation
directory. Default is the src folder under the source
path(RezBuilder.source_path).

### InstallBuilder(mode=None)

Abstract Base Classes, all builders that require installation files are
inherited from this class.

mode(int): The search mode of get installers. Now only support local
mode(InstallBuilder.LOCAL). Default is the local mode.

### InstallBuilder.LOCAL

int: Mode flag. This flag indicates that using local mode. Local mode will
search a local path to get the installers. 

REZBUILD_SEARCH_MODE: Environment variables, used to set the search mode.
`InstallBuilder` will get this value if the mode parameter is not provided
during initialization. Default is the local mode if the environment variables
is not provided.

Supported value:
- 0 -- local mode

### InstallBuilder.get_installers(local_path=None, regex=None) -> list(str)

Search the specified place and return a list of installation file path that
required the satisfied. Will return the file for the current variant if the
package has more than on variants. The default search path is the folder named
installers under the source root(InstallBuilder.source_root) in local
mode(`InstallBuilder.LOCAL`) if `local_path` is not specified.

All the files will be list in the result. Pass a regex to the `regex` parameter
will return the files that only file name match it.

Multi-variant package will search the folder that name same with the variant
index first if the folder exist in the search path. The tree should like this:

```text
source_root/
├── build.py
├── package.py
└── installers/
    ├── 0/
    │   ├── installer1
    │   ├── installer2
    │   └── installer3
    └── 1/
        ├── installer4
        └── installer5

```

local_path(str): Specify the installation file search path. Default is the 
folder named installers under the source root(InstallBuilder.source_root).
Local mode only. 

regex(str): The regular expression to match the installation files. Only the
file that name match the expression will be return if the parameter not empty.

### ExtractBuilder()

This builder will extract the archive file and copy the content into install
path(`RezBuilder.install_path`).

### ExtractBuilder.extract(extract_path, installer_regex=None) -> None

Extract archive into the specified path(`extract_path`).

extract_path(str): Target path to put the files that extract from the archive.

installer_regex(str): The regular expression to match the installation files.
Only the file that name match the expression will be extracted.

### ExtractBuilder.get_installers(local_path=None, regex=None) -> list(str)

Inherit from `InstallBuilder.get_installers`.

### ExtractBuilder.build(extract_path=None, installer_regex=None, dirs_exist_ok=True, follow_symlinks=True, file_overwrite=False) -> None

Extract archive files and copy into the installation
path(`RezBuilder.install_path`).

extract_path(str): Where to put the files that extract from the archive.
Default is using the temporary folder.

installer_regex(str): The regular expression to match the installation files.
Only the file that name match the expression will be extracted. Extract all the
archive files that `get_installers` returned if not provided.

dirs_exist_ok(bool): Whether to merge the same name folder when copy files.
`True` will merge the directories, `False` will raise an exception. 

follow_symlinks(bool): If follow_symlinks is false and src is a symbolic link,
a new symbolic link will be created instead of copying the file src points to.

file_overwrite(bool): Whether to overwrite the file with the same name. `True`
will overwrite, otherwise `False`.

### CompileBuilder()

Extract source archive file, compile and copy to installation directory.
The source archive file format should be zip or tar.gz.

### CompileBuilder.build(extra_config_args=None, installer_regex=None, install_path=None, make_movable=False) -> None

Build the package.

extra_config_args(list(str)): configure arguments。

installer_regex(str): The regular expression to match the archive files.
Only the file that name match the expression will be extracted.

install_path(str): Specify the path to put the compiled file. Default is the
workspace(RezBuilder.workspace).

### CompileBuilder.compile(source_path, install_path, extra_config_args=None) -> None

Compile source code by configure and make command.

source_path(str): Where the source code placed.

install_path(str): Where to put the compiled file.

extra_config_args(list(str)): configure arguments.

### CompileBuilder.get_installers(local_path=None, regex=None) -> list(str)

Inherit from InstallBuilder.get_installers

## MacOSBuilder()

Abstract Base Classes, all the macOS builder inherit from this class.

### MacOSBuilder.create_open_shell(app_name, path, shell_name="") -> None

Create a shell script to open the macOS app.

app_name(str): macOS app name.

path(str): Directory to put the shell script.

shell_name(str): Shell name. Default is the app_name replaced the space to
underscore.

### MacOSBuilder.extract_dmg(dmg_file, extract_path) -> None

Extract the macOS installation file with dmg format.

dmg_file(str): dmg file.

extract_path(str): Directory to put the extract files.

### MacOSBuilder.extract_pkg(pkg_file, extract_path) -> None

Extract the macOS installation file with pkg format.

pkg_file(str): pkg file.

extract_path(str): Directory to put the extract files.

### MacOSDmgBuilder()

Build package from dmg installation file.

### MacOSDmgBuilder.build(create_shell=True, shell_name="")

Build the package.

create_shell(str): Whether to create shell script.

shell_name(str): Specify shell name. Only takes effect when create_shell is
`True`.

### PythonBuilder()

Abstract Base Classes, all the python builder inherit from this class.

### PythonBuilder.change_shebang(root="", shebang="")

Modified the shebang of entry_points. entry_point will hardcode the python path
when pip install the wheel file. This method will modify the shebang to get the
python executable from environment.

root(str): entry_point directory。All the files under this directory will be
checked and modified the shebang.

shebang(str): Specify the value of shebang to change to. On Windows, default is
`#!python(w).exe`. On macOS, default is `#!/usr/bin/env python`.

### PythonBuilder.install_wheel(wheel_file, install_path="", change_shebang=False, shebang="") -> None

Installation wheel file.

wheel_file(str): Wheel file to install.

install_path(str): Directory to install wheel. Default is
`RezBuilder.workspace`.

change_shebang(bool): Whether to modify the shebang of entry point. Default is
`False`.

shebang(str): Specify the value of shebang to change to. On Windows, default is
`#!python(w).exe`. On macOS, default is `#!/usr/bin/env python`.

### PythonSourceBuilder()

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

### PythonSourceBuilder.build(change_shebang=False, use_venv=True, shebang="") -> None

Build the package.

change_shebang(bool): Whether to modify the shebang of entry point. Default is
`False`.

use_venv(bool): Whether to use venv when build wheel file. Default is `True`. 

shebang(str): Specify the value of shebang to change to. On Windows, default is
`#!python(w).exe`. On macOS, default is `#!/usr/bin/env python`.

### PythonSourceArchiveBuilder()

Build package by python source archive file.

### PythonSourceArchiveBuilder.build(change_shebang=False, use_venv=True, shebang="") -> None

change_shebang(bool): Whether to modify the shebang of entry point. Default is
`False`.

use_venv(bool): Whether to use venv when build wheel file. Default is `True`.

shebang(str): Specify the value of shebang to change to. On Windows, default is
`#!python(w).exe`. On macOS, default is `#!/usr/bin/env python`.

### PythonWheelBuilder()

Build package by python wheel file.

### PythonWheelBuilder.build(change_shebang=False, shebang="") -> None

change_shebang(bool): Whether to modify the shebang of entry point. Default is
`False`.

shebang(str): Specify the value of shebang to change to. On Windows, default is
`#!python(w).exe`. On macOS, default is `#!/usr/bin/env python`.

### Environment variables

REZBUILD_SEARCH_MODE: Environment variables, used to set the search mode.
`InstallBuilder` will get this value if the mode parameter is not provided
during initialization. Default is the local mode if the environment variables
is not provided.

Supported value:
- 0 -- local mode

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available,
see the [tags on this repository](https://gitlab.com/Pili-Pala/rezbuild/tags).

## Author
[PiliPala](https://gitlab.com/Pili-Pala)

## License
[GPLv3](https://www.gnu.org/licenses/gpl-3.0.txt)

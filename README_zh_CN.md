# Rezbuild

Rezbuild 是一个 Rez 的包构建工具. 若想了解 Rez 请访问
[Rez 官方网站](https://github.com/nerdvegas/rez) 。

Please visit
[here](https://gitlab.com/Pili-Pala/rezbuild/-/blob/main/README.md)
to get the english document.

## 简介

### 使用场景

This project is a build tool to build rez packages. We always need to do some
of the same steps when we build a rez package. Just like extract zip file,
install the wheel file using pip, copy files to the installation directory. The
goal of this project is to cover all the repetitive work when building rez
package.

## 教程

### 依赖项

Rezbuild requires the python-3.6+, build-0.3+(lower version did not test) and
pip-18+ to run. If you want to install this package from source, git and
setuptools_scm are also needed.

### 如何安装

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

But as this package is for rez, it doesn't make sense in most of the time.

## 测试

### Break down into end to end tests

### And coding style tests

## 使用方式

## 版本管理

We use [SemVer](http://semver.org/) for versioning. For the versions available,
see the [tags on this repository](https://gitlab.com/Pili-Pala/rezbuild/tags).

## 作者
[噼里啪啦](https://gitlab.com/Pili-Pala)

## 软件许可
[GPLv3](https://www.gnu.org/licenses/gpl-3.0.txt)

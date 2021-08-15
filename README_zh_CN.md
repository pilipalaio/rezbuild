# Rezbuild

Rezbuild 是一个 Rez 的包构建工具。 若想了解 Rez 请访问
[Rez 官方网站](https://github.com/nerdvegas/rez) 。

Please visit
[here](https://gitlab.com/Pili-Pala/rezbuild/-/blob/main/README.md)
to get the english document.

## 简介

### 使用场景

rezbuild 是一个用于构建 rez 包的构建工具。我们在构建 rez 
包时通常有很多相似的步骤，比如解压缩 zip 文件，使用 pip 安装 wheel 
文件，拷贝文件到安装目录等等。rezbuild 用于简化所有相似的安装步骤，让我们在安装 rez 
包的时候只需要关注安装逻辑即可。

## 教程

### 依赖项

rezbuild 只能在 python-3.6 及以上版本运行，同时需要 build-0.3 及以上版本（0.3
以下的版本未经过测试，不保证一定能运行），pip-18 及以上版本。如果需要从源代码安装 
rezbuild，则构建时还 需要 git 和 setuptools_scm。

### 如何安装

1.通过自己安装(需要环境中有其他版本的 rezbuild)

rezbuild 
可以自己安装自己，这也是推荐的方式。请确保所有的依赖项都已安装到您的环境中，包括 
rezbuild（旧版本即可）。
请从  [PyPI](https://pypi.org/project/rezbuild/#files) 下载官方 wheel 
文件，并创建如下目录：

```text
install_rezbuild/
    |___installers/
        |___rezbuild-0.5.0-py3-none-any.whl
    |___build.py
    |___package.py
```

build.py 的内容如下：

```python
# build.py
from rezbuild.builder import PythonWheelBuilder


if __name__ == '__main__':
    builder = PythonWheelBuilder()
    builder.build()
```

package.py 的内容如下：

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

进入根目录（install_rezbuild），并运行如下命令：`rez build -i`
当命令执行完成后，该包就已作为 rez 包安装完成了。

2.从源代码安装

如果你第一次使用 rezbuild，或你的系统中没有其他版本的 rezbuild，你也可以通过源代码来安装
rezbuild。请确保所有依赖项均已安装(python-3.6+，build-0.3+，pip-18+，
[git，setuptools_scm])。如果系统中没有 setuptools_scm，也可以手动将 `package.py` 中的
`version` 字段改为对应版本。该字段的默认行为是自动通过 setuptools_scm 来获取正确的版本号。

然后 clone 这个项目，进入代码根目录并运行构建命令即可，范例命令如下：

```shell
git clone git@gitlab.com:Pili-Pala/rezbuild.git
cd rezbuild
rez build -i
```

3.通过 PyPI 安装

当然，你也可以通过 pip 来安装 rezbuild：

```shell
pip install rezbuild
```

但考虑到此工具专用于 rez，绝大多数时候这么做是没什么意义的。

## 使用方式

Rez 在 2.70.0 版本后移除了 bez 构建工具，本文档指包含该版本后的使用方式。

Rezbuild 支持多种不同的构建途径，可以从 whl 文件构建 python 
包，也可以从源代码开始构建，或者你也可以自定义构建方式。

### 由 python wheel 文件构建 rez 包(PythonWheelBuilder)

我假设你了解 rez 是什么，如何制作 package.py 文件，且你现在想制作一个第三方的 python 包。

首先，添加一个名为 `build.py` 的 python 文件到构建根目录，内容如下：

```python
# Import third-party modules
from rezbuild import PythonWheelBuilder


if __name__ == '__main__':
    PythonWheelBuilder().build()
```

然后，在 `package.py` 文件中增加一个 `build_command` 变量，例如：
`build_command = 'python {root}/build.py {install}'`.

从 [PyPI](https://pypi.org) 下载你需要安装的包的 wheel 文件，放到 
`source_root/installer` 目录下。目录结构如下：

```text
source_root/
    |___installers/
        |___the_package_you_want_to_install.whl
    |___build.py
    |___package.py
```

最后，将当前目录切换到 `source_root` 然后执行构建命令 `rez build -i`，该 rez 
包即会自动安装完成。

### 由 python 源代码构建包(PythonSourceBuilder)

与构建 wheel 包的不同之处仅仅只是 builder 的名字。将 builder 改为 `PythonSourceBuilder`
即可。如下：

```python
# Import third-party modules
from rezbuild import PythonSourceBuilder


if __name__ == '__main__':
    PythonSourceBuilder().build()
```

在运行构建命令前请确保你已经添加了所有构建 python 包的必要文件
[tutorial](https://packaging.python.org/tutorials/packaging-projects/)。
`PythonSourceBuilder` 会调用 python 官方默认的构建方式 build 来构建包。

### 由归档文件构建(ExtractBuilder)

`build.py` 文件如下：

```python
# Import third-party modules
from rezbuild import ExtractBuilder


if __name__ == '__main__':
    ExtractBuilder().build()
```

将归档文件放置于 `installers` 文件夹。

```text
source_root/
    |___installers/
        |___archive.zip
    |___build.py
    |___package.py
```

在 `source_root` 下执行命令 `rez build -i`。

### 由源代码编译构建(CompileBuilder)

`build.py` 如下：

```python
# Import third-party modules
from rezbuild import CompileBuilder


if __name__ == '__main__':
    CompileBuilder().build()
```

Put source archive file into installers folder.

```text
source_root/
    |___installers/
        |___git-2.32.0.tar.gz
    |___build.py
    |___package.py
```

Run command `rez build -i` from `source_root`.

### 自定义 builder

你也可以自定义 builder。只需要从默认 builder 继承并重写 `custom_build`
函数即可。下边将简单介绍 rezbuild 的默认 builder 以方便你自定义自己的 builder。 

#### RezBuilder
`RezBuilder` 是根 builder，所有其他 builder 都继承自它。此 builder 负责捕获 rez
环境变量，确认工作目录，将构建好的包安装到系统中，以及执行你的自定义构建函数。

使用样例：
```python
# Import built-in modules
import os
import shutil

# Import third-party modules
from rezbuild import RezBuilder


class CustomBuilder(RezBuilder):

    def custom_build(self, copy=False):
        if copy:
            shutil.copytree(
                os.path.join(self.source_path, "src"), self.build_path)


if __name__ == '__main__':
    CustomBuilder().build(copy=True)
```

`build` 函数会调用自定义构建函数 `custom_build` 来构建包。

### 多变种包的安装
如果您安装的软件涉及多个变种(variants)，且每个变种的安装包都是独立的，则您的可以在
`installers` 文件夹下创建以变种索引(variant
index)命名的文件夹，并在文件夹下放置对应安装包。例如：

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

当构建到该变种时，rezbuild 即会自动抓取到目录下的所有安装包。

## 版本管理

此项目使用 [语义化版本](http://semver.org/) 来规范版本命名。可以访问
[此项目的所有 tag](https://gitlab.com/Pili-Pala/rezbuild/tags) 来查看所有可用版本。

## 作者
[噼里啪啦](https://gitlab.com/Pili-Pala)

## 软件许可
[GPLv3](https://www.gnu.org/licenses/gpl-3.0.txt)

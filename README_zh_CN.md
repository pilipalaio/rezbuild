# Rezbuild

Rezbuild 是一个 Rez 的包构建工具. 若想了解 Rez 请访问
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

1.通过自己安装

rezbuild 
可以自己安装自己，这也是推荐的方式。请确保所有的依赖项都已安装到您的环境中，包括 
rezbuild（旧版本即可）。
请从  [PyPI](https://pypi.org/project/rezbuild/#files) 下载官方 wheel 
文件，并创建如下目录：

```text
install_rezbuild/
    |___rez_installers/
        |___0/
            |___rezbuild-0.2.0-py3-none-any.whl
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

package.py 的内容如下:

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

进入根目录（install_rezbuild），并运行如下命令：
`rez build -i`

当命令执行完成后，该包就已作为 rez 包安装完成了。

2.从源代码安装

如果你第一次使用 rezbuild，或你的系统中没有旧版本的 rezbuild，你也可以通过源代码来安装
rezbuild。请确保所有依赖项均已安装(python-3.6+, build-0.3+, pip-18+,
[git, setuptools_scm])。如果系统中没有 setuptools_scm，也可以手动将 `package.py` 中的
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

## 测试

### Break down into end to end tests

### And coding style tests

## 使用方式

## 版本管理

此项目使用 [语义化版本](http://semver.org/) 来规范版本命名。可以访问
[此项目的所有 tag](https://gitlab.com/Pili-Pala/rezbuild/tags) 来查看所有可用版本.

## 作者
[噼里啪啦](https://gitlab.com/Pili-Pala)

## 软件许可
[GPLv3](https://www.gnu.org/licenses/gpl-3.0.txt)

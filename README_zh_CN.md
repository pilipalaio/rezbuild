# Rezbuild

Rezbuild 是一个 Rez 的包构建工具.  若想了解 Rez 请访问
[Rez 官方网站](https://github.com/nerdvegas/rez) . 

Please visit
[here](https://gitlab.com/Pili-Pala/rezbuild/-/blob/main/README.md)
to get the english document.

## 简介

rezbuild 是一个用于构建 rez 包的工具. rezbuild 用于简化 rez 包的构建方式, 让我们在安装 rez 
包的时候只需要关注安装逻辑即可. 

rezbuild 支持通过 python wheel 文件、python source archive 文件、python源代码、
归档文件、unix 源代码、macOS pkg 和 macOS dmg 文件构建 rez 包.

## 安装

### 依赖项

rezbuild 只能在 python-3.6 及以上版本运行, 同时需要 build-0.3 及以上版本（0.3
以下的版本未经过测试）, pip-18 及以上版本. 

### 安装方式

请根据实际情况从以下三种安装方式中选择.

#### 1.从源代码安装(适用于未使用过 rezbuild, 或者系统中没有 rezbuild 的用户)

如果你第一次使用 rezbuild, 或你的系统中没有其他版本的 rezbuild, 你可以通过源代码来安装
rezbuild. 请确保所有依赖项均已安装(python-3.6+, build-0.3+, pip-18+). 

然后 clone 这个项目, 进入代码根目录并运行构建命令: 

```shell
git clone git@gitlab.com:Pili-Pala/rezbuild.git
cd rezbuild
rez build -i
```

#### 2.通过自身安装(需要环境中有其他版本的 rezbuild)

rezbuild 
可以自己安装自己. 请确保所有的依赖项都已安装到您的环境中, 包括 rezbuild(旧版本即可). 
请从  [PyPI](https://pypi.org/project/rezbuild/#files) 下载 wheel 
文件, 并创建如下目录: 

```text
install_rezbuild/
├── build.py
├── package.py
└── installers/
    └── rezbuild-0.14.1-py3-none-any.whl

```

build.py 的内容如下: 

```python
# build.py
from rezbuild.builder import PythonWheelBuilder


if __name__ == '__main__':
    PythonWheelBuilder().build()

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

进入根目录（install_rezbuild）, 并运行如下命令: `rez build -i`.
当命令执行完成后, 该包就已作为 rez 包安装完成了.


#### 3.通过 PyPI 安装

当然, 你也可以通过 pip 来安装 rezbuild: 

```shell
pip install rezbuild
```

但考虑到此工具专用于 rez, 绝大多数时候这么做是没什么意义的. 

## 使用方式

Rez 在 2.70.0 版本后移除了 bez 构建工具, 本软件只支持该版本后的使用方式.

### 通过 python wheel 文件构建 rez 包(PythonWheelBuilder)

我假设你了解 rez 是什么, 如何制作 package.py 文件, 且你现在想制作一个第三方的 python 包. 

首先, 添加一个名为 `build.py` 的 python 文件到构建根目录, 内容如下: 

```python
# Import third-party modules
from rezbuild import PythonWheelBuilder


if __name__ == '__main__':
    PythonWheelBuilder().build()

```

然后, 在 `package.py` 文件中增加一个 `build_command` 变量, 例如: 
`build_command = 'python {root}/build.py {install}'`.

从 [PyPI](https://pypi.org) 下载你需要安装的包的 wheel 文件, 放到 
`source_root/installer` 目录下. 目录结构如下: 

```text
source_root/
├── build.py
├── package.py
└── installers/
    └── the_package_you_want_to_install.whl
```

最后, 将当前目录切换到 `source_root` 然后执行构建命令 `rez build -i`, 该 rez 
包即会自动安装完成. 

### 由 python 源代码构建包(PythonSourceBuilder)

`PythonSourceBuilder` 用于构建符合 python 官方结构要求的源代码包. 代码结构请参考
[python 官网教程](https://packaging.python.org/en/latest/tutorials/packaging-projects/).
目录结构应如下: 

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

`build.py` 应如下: 

```python
# Import third-party modules
from rezbuild import PythonSourceBuilder


if __name__ == '__main__':
    PythonSourceBuilder().build()

```

在运行构建命令前请确保你已经添加了所有构建所需的必要文件. 
`PythonSourceBuilder` 会调用 python 官方构建方式来构建包. 

最后, 将当前目录切换到 `source_root` 然后执行构建命令 `rez build -i`, 该 rez
包即会构建并安装.

### 由 python 源代码归档文件构建(PythonSourceArchiveBuilder)

有些包并未在 PyPI 上提供构建好的 wheel 文件, 仅提供了 python 源代码归档文件(source
archive), 此时我们可以将 builder 换成 PythonSourceArchiveBuilder 来进行构建. 

### 拷贝构建(CopyBuilder)

有时候我们不需要完整走完 python 官方的构建流程(不走完流程会缺少 metadata 等), 仅需要拷贝代
码. 使用 CopyBuilder 即可完成单纯的拷贝构建. 默认会从源代码根目录下的 src 文件夹中拷贝, 若需
自定义该目录则需要将目标目录传递给 build 方法的 root 参数. build.py 文件如下: 

```python
# Import third-party modules
from rezbuild import CopyBuilder


if __name__ == '__main__':
    CopyBuilder().build(root="/path/to/source")

```

### 由归档文件构建(ExtractBuilder)

当安装包为归档文件时, 可以使用 ExtractBuilder 解压缩归档文件来构建. ExtractBuilder 目前支
持 zip, tar.gz, tar.xz 和 7z.exe 格式的归档文件.   

`build.py` 文件如下: 

```python
# Import third-party modules
from rezbuild import ExtractBuilder


if __name__ == '__main__':
    ExtractBuilder().build()

```

将归档文件放置于 `installers` 文件夹. 

```text
source_root/
├── build.py
├── package.py
└── installers/
    └── archive.zip

```

### 由源代码编译构建(CompileBuilder)

CompileBuilder 支持在 Linux 和 macOS 下使用 `configure` 和 `make` 命令进行编译构建. 
configure 命令的参数通过 build 方法的 extra_config_args 传递. 

`build.py` 如下: 

```python
# Import third-party modules
from rezbuild import CompileBuilder


if __name__ == '__main__':
    CompileBuilder().build(extra_config_args=["LDFLAGS=-L/path/to/lib"])

```

将打包好的源代码文件放到 installers 文件夹中. 

```text
source_root/
├── build.py
├── package.py
└── installers/
    └── git-2.32.0.tar.gz

```

### 由 macOS dmg file 构建包(MacOSDmgBuilder)

```python
# Import third-party modules
from rezbuild import MacOSDmgBuilder


if __name__ == '__main__':
    MacOSDmgBuilder().build()

```

将 dmg 文件放入 installers 文件夹中，结构如下：

```text
source_root/
├── build.py
├── package.py
└── installers/
    └── installer.dmg
```

从 `source_root` 执行命令 `rez build -i`.

`MacOSDmgBuilder` 会在安装目录下创建一个 shell 脚本, has a same
with the `.app` folder. Set `create_shell` to `False` to prevent his creation.
For example: `MacOSDmgBuilder().build(create_shell=False)`

### 自定义 builder

你也可以自定义 builder. 只需要从默认 builder 继承并重写 `custom_build`
函数即可. 下边将简单介绍 rezbuild 的默认 builder 以方便你自定义自己的 builder.  

#### RezBuilder
`RezBuilder` 是根 builder, 所有其他 builder 都继承自它. 此 builder 负责捕获 rez
环境变量, 确认工作目录, 将构建好的包安装到系统中, 以及执行你的自定义构建函数. 

使用样例: 
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

`build` 函数会调用自定义构建函数 `custom_build` 来构建包. 

### 多变种包的安装
如果您安装的软件涉及多个变种(variants), 且每个变种的安装包都是独立的, 则您的可以在
`installers` 文件夹下创建以变种索引(variant
index)命名的文件夹, 并在文件夹下放置对应安装包. 例如: 

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

当构建到该变种时, rezbuild 即会自动抓取到目录下的所有安装包. 

## API

### builder 模块

### RezBuilder()

`RezBuilder` 是根 builder, 所有其他 builder 都继承自它. 此 builder 负责捕获 rez
环境变量, 确认工作目录, 将构建好的包安装到系统中, 以及执行你的自定义构建函数. 

### RezBuilder.build_path

构建目录. rez 默认构建位置.

### RezBuilder.install_path

安装目录. 默认为 ~/packages.

### RezBuilder.source_path

源代码根目录.

### RezBuilder.workspace

工作空间. 该目录下的所有文件及文件夹会被完整的拷贝到安装目录中.

### RezBuilder.name

包名.

### RezBuilder.version

构建版本.

### RezBuilder.variant_index

变体索引.

### RezBuilder.build(**kwargs) -> None

构建方法, 触发构建流程. 该方法会调用子类的 custom_build 方法来执行具体的构建.

kwargs: 接受所有命名参数并传递给 custom_build 方法.

### CopyBuilder() -> None

拷贝目标文件夹的所有文件到包的安装目录中(this.root).

### CopyBuilder.build(root) -> None

root: 此目录下的所有文件都会被拷贝到安装目录中. 默认为源代码目录下的src文件夹.

### InstallBuilder(mode=None)

基类, 所有需要安装文件的 builder 都继承于此类.

mode(int): 获取安装文件的模式. 目前仅支持本地模式(InstallBuilder.LOCAL). 若不指定则默认为
本地模式.

InstallBuilder.LOCAL(int): 模式标识, 此标识表示安装包的获取模式为本地模式.

REZBUILD_SEARCH_MODE: 环境变量, 用于指定默认搜索模式. 若在初始化 InstallBuilder 时未指定
mode 参数, 则抓取此环境变量设置的值. 当使用本地模式(InstallBuilder.LOCAL)时,
应将此环境变量设置为0. 目前仅支持本地模式. 若未指定环境变量则默认为本地模式.

### InstallBuilder.get_installers(local_path=None, regex=None) -> list(str)

搜索指定目录, 返回一个包含所有符合要求的安装文件完整路径的列表. 若有多个变体(variant), 
则会获取当前变体的安装文件. 本地模式下(InstallBuilder.LOCAL), 若不指定 local_path, 
则搜索目录默认为源代码根目录下 installers 文件夹. 

搜索目录下的所有文件均会被列出并返回. 若需要控制文件的匹配规则, 可以使用 regex
函数传入正则表达式, 匹配正则表达式的安装文件名才会被返回. 

含有变体(variants)的包会优先寻找搜索目录下是否含有与变体索引(REZ_BUILD_VARIANT_INDEX)
同名的文件夹, 若有则返回变体索引目录下的安装包, 若没有则返回搜索目录下的安装包. 目录结构应如下:

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

local_path(str): 指定安装文件搜索路径, 若不指定默认为源代码根目录下 installers 文件夹.

regex(str): 安装文件的正则表达式, 若该字段不为空,
则只有文件名匹配提供的正则表达式的安装文件才会被返回.

### ExtractBuilder()

解压缩归档文件并拷贝到安装目录.

### ExtractBuilder.extract(extract_path, installer_regex=None) -> None

将压缩包解压到指定路径(extract_path).

extract_path(str): 解压文件放置的目标路径.

installer_regex(str): 归档文件名的正则表达式, 只有匹配表达式的归档文件才会被解压缩.

### ExtractBuilder.get_installers(local_path=None, regex=None) -> list(str)

继承自 InstallBuilder.get_installers.

### ExtractBuilder.build(extract_path=None, installer_regex=None, dirs_exist_ok=True, follow_symlinks=True, file_overwrite=False) -> None

解压缩归档文件并拷贝到安装目录.

extract_path(str): 文件的解压缩路径, 若为空则使用临时文件夹.

installer_regex(str): 归档文件正则表达式. 文件名与正则表达式匹配的文件才会被解压. 
若不提供默认解压则缩所有 get_installers 所返回的文件.

dirs_exist_ok(bool): 当有多个文件被解压并拷贝到安装目录时, 同名文件夹是否合并, 若为 False 则出现同
名文件夹时报错. 

follow_symlinks(bool): 如果 follow_symlinks 为假值且 src 为符号链接,
则将创建一个新的符号链接而不是拷贝 src 所指向的文件. 

file_overwrite(bool): 拷贝时同名文件是否进行覆盖. 

### CompileBuilder()

解压缩源代码归档文件, 编译并拷贝到安装目录. 源代码包应为 zip 或 tar.gz 等归档格式, 并保证
get_installers 方法可以获取到

### CompileBuilder.build(extra_config_args=None, installer_regex=None, install_path=None, make_movable=False) -> None

构建命令。解压缩源代码归档文件，编译并安装到指定位置。

extra_config_args(list(str)): configure 参数。

installer_regex: 归档文件正则表达式. 文件名与正则表达式匹配的文件才会被解压.

install_path: 指定安装路径。若为空则默认为 workspace.

### CompileBuilder.compile(source_path, install_path, extra_config_args=None) -> None

使用 configure 和 make 命令编译源代码.

source_path(str): 源代码所在根目录.

install_path(str): 编译后文件的安装位置.

extra_config_args(list(str)): configure 参数.

### CompileBuilder.get_installers(local_path=None, regex=None) -> list(str)

继承自 InstallBuilder.get_installers

## MacOSBuilder()

基类. 所有 macOS 系统的 builder 都继承于此.

### MacOSBuilder.create_open_shell(app_name, path, shell_name="") -> None

创建一个可以打开指定 macOS app 的 shell 脚本. 

app_name: macOS app 的名字.

path: 脚本存放目录.

shell_name: 指定脚本的名字。默认为 app_name.

### MacOSBuilder.extract_dmg(dmg_file, extract_path) -> None

解压缩 dmg 格式的 macOS 安装文件.

dmg_file: dmg 安装文件的路径.

extract_path: 解压缩文件的存放位置.

### MacOSBuilder.extract_pkg(pkg_file, extract_path) -> None

解压缩 pkg 格式的 macOS 安装文件.

pkg_file: pkg 安装文件的路径.

extract_path: 解压缩文件的存放位置.

### MacOSDmgBuilder()

从 dmg 格式的安装文件构建包.

### MacOSDmgBuilder.build(create_shell=True, shell_name="")

触发构建.

create_shell(str): 是否创建启动 shell.

shell_name(str): create_shell 为真时使用. 指定 shell 名.

### PythonBuilder()

基类, 所有 python 相关 builder 均继承于此.

### PythonBuilder.change_shebang(root="", shebang="")

修改 python entry_point 中的 shebang. pip 安装 wheel 时创建的 entry_point 文件会记录
python 的绝对路径。此方法可以修改该路径为抓取环境中指定的 python.

root(str): entry_point 文件所在目录。该目录下所有文件均会被检测并修改 shebang.

shebang(str): 指定 shebang 被修改为何值. 如不提供, windows 下默认为
`#!python(w).exe`, macOS 下默认为 #!/usr/bin/env python.

### PythonBuilder.install_wheel(wheel_file, install_path="", change_shebang=False, shebang="") -> None

安装 wheel 文件.

wheel_file(str): 要安装的 wheel 文件的路径.

install_path(str): 安装目录. 默认为 PythonBuilder.workspace.

change_shebang(bool): 是否修改 entry point 中的 shebang. 默认为假.

shebang(str): 指定 shebang 被修改为何值. 如不提供, windows 下默认为
`#!python(w).exe`, macOS 下默认为 #!/usr/bin/env python.

### PythonSourceBuilder()

用于构建符合 python 官方结构要求的源代码包. 代码结构请参考
[python 官网教程](https://packaging.python.org/en/latest/tutorials/packaging-projects/).
目录结构应如下:

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

触发构建.

change_shebang(bool): 是否修改 entry_point 文件中的 shebang. 默认为假.

use_venv(bool): 是否使用虚拟环境构建包。默认为真.

shebang(str): 指定 shebang 被修改为何值. 如不提供, windows 下默认为
`#!python(w).exe`, macOS 下默认为 #!/usr/bin/env python.

### PythonSourceArchiveBuilder()

通过 python source archive 文件构建 rez 包.

### PythonSourceArchiveBuilder.build(change_shebang=False, use_venv=True, shebang="") -> None

change_shebang(bool): 是否修改 entry_point 文件中的 shebang. 默认为假.

use_venv(bool): 是否使用虚拟环境构建包。默认为真.

shebang(str): 指定 shebang 被修改为何值. 如不提供, windows 下默认为
`#!python(w).exe`, macOS 下默认为 #!/usr/bin/env python.

### PythonWheelBuilder()

通过 python wheel 文件构建 rez 包.

### PythonWheelBuilder.build(change_shebang=False, shebang="") -> None

change_shebang(bool): 是否修改 entry_point 文件中的 shebang. 默认为假.

shebang(str): 指定 shebang 被修改为何值. 如不提供, windows 下默认为
`#!python(w).exe`, macOS 下默认为 #!/usr/bin/env python.

## 版本管理

此项目使用 [语义化版本](http://semver.org/) 来规范版本命名. 可以访问
[此项目的所有 tag](https://gitlab.com/Pili-Pala/rezbuild/tags) 来查看所有可用版本. 

## 作者
[噼里啪啦](https://gitlab.com/Pili-Pala)

## 软件许可
[GPLv3](https://www.gnu.org/licenses/gpl-3.0.txt)

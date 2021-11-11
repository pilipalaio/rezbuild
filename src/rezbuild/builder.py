"""This module include some rez builders.

Rez builder help to build rez packages.

1. RezBuilder
    The basic class of all the builder derivatives.

2. InstallBuilder
    The basic builder for build package from the installers, like
    `.exe` or `.dmg`.

3. PythonBuilder
    The basic builder for build python package.

3. PythonSourceBuilder
    The basic builder for build package from python source code.

4. PythonWheelBuilder
    This is the builder for build python package from wheel file.
"""

# Import built-in modules
import abc
import os
import platform
import re
import shutil
import stat
import subprocess
import tarfile
import tempfile
import zipfile

# Import local modules
from rezbuild.bin_utils import make_bins_movable
from rezbuild.constant import SHELL_CONTENT
from rezbuild.exceptions import ArgumentError
from rezbuild.exceptions import UnsupportedError
from rezbuild.utils import clear_path
from rezbuild.utils import get_delimiter
from rezbuild.utils import remove_tree


class RezBuilder(abc.ABC):
    """The basic class of RezBuild."""

    def __init__(self, **kwargs):
        """Initialize builder."""
        self.build_path = os.environ["REZ_BUILD_PATH"]
        self.install_path = os.environ["REZ_BUILD_INSTALL_PATH"]
        self.name = os.environ["REZ_BUILD_PROJECT_NAME"]
        self.version = os.environ["REZ_BUILD_PROJECT_VERSION"]
        self.source_path = os.environ["REZ_BUILD_SOURCE_PATH"]
        self.variant_index = os.environ["REZ_BUILD_VARIANT_INDEX"]
        self.workspace = os.path.join(self.build_path, "workspace")
        # self.temp_dirs list all the temporary directory objects that create
        # by tempfile.
        self.temp_dirs = []
        super().__init__(**kwargs)

    def build(self, **kwargs):
        """Build the package."""
        self.create_work_dir()
        self.custom_build(**kwargs)
        self.install()
        self.clean_temp_dir()

    def clean_temp_dir(self):
        """Clean all the temp dir."""
        for temp_dir in self.temp_dirs:
            temp_dir.cleanup()

    def create_work_dir(self):
        """Create the work directory.

        If the work directory already exists, remove the old one and create it.
        """
        if os.path.exists(self.workspace):
            remove_tree(self.workspace)
        os.makedirs(self.workspace)

    def custom_build(self, **kwargs):
        """Execute custom build method.

        Raises:
            NotImplementedError: When this method does not implemented by the
                child class.
        """
        raise NotImplementedError(
            "This method does not implemented by the invoker.")

    def install(self):
        """Copy files from work directory to self.install_path."""
        if os.environ.get("REZ_BUILD_INSTALL") == "1":
            if os.path.exists(self.install_path):
                remove_tree(self.install_path)
            shutil.copytree(self.workspace, self.install_path, symlinks=True)


class InstallBuilder(RezBuilder, abc.ABC):
    """This class is the base builder to build package from installer."""

    # Class constants to mark up where the installers come from. Default is
    # LOCAL.
    LOCAL = 0
    PYPI = 1

    def __init__(self, mode=None, **kwargs):
        """Initialize the builder.

        Args:
            mode (int): The installer search mode to set.
                InstallerBuilder.LOCAL -- 0
                InstallerBuilder.PYPI -- 1
        """
        self._search_mode = None
        self._init_search_mode(mode)
        super().__init__(**kwargs)

    def _init_search_mode(self, mode):
        """Initialize the search mode.

        Prioritize `mode` if it is supported, then get the
        `REZBUILD_SEARCH_MODE` environment variable if given, finally set the
        InstallerBuilder.LOCAL as the default.

        Args:
            mode (int): The installer search mode to set.
                InstallerBuilder.LOCAL -- 0
                InstallerBuilder.PYPI -- 1

        Raises:
            ArgumentError: When the installer search mode does not support.
        """
        mode = mode or int(
            os.getenv("REZBUILD_SEARCH_MODE", self.__class__.LOCAL))
        if mode in self.list_modes():
            self._search_mode = mode
        else:
            raise ArgumentError(f"Mode {self._search_mode} unsupported.")

    def get_installers(self, local_path=None, regex=None):
        """Get installers.

        In `InstallerBuilder.LOCAL` mode, the default place is a folder named
        "installers" under the source root. You can put the installers into the
        installers folder, or if the different variant has different installer,
        put its into variant folders. Each variants has a folder named with its
        "REZ_BUILD_VARIANT_INDEX" under the installers directory. The directory
        structure should like this:

        source_root/
            |___installers/
                |___installer1
                |___installer2
                |___installer3
                |___installer4

        Or like this:

        source_root/
            |___installers/
                |___0/
                    |___installer1
                    |___installer2
                    |___installer3
                |___1/
                    |___installer4
                    |___installer5

        Args:
            local_path (str): The directory where the installers placed.
                This will be used when the installer_search_mode is
                `InstallerBuilder.LOCAL`.
            regex (str): The regex string to match the installer name.

        Returns:
            :obj:`list` of :obj:`str`: All the paths of the installers.

        Raises:
            ArgumentError: When the installer search mode does not support.
        """
        regex = regex or r".*"
        exclude_files = [".DS_Store"]
        if self._search_mode == self.__class__.LOCAL:
            if local_path:
                path = os.path.join(local_path, self.variant_index)
            else:
                path = os.path.join(
                    self.source_path, "installers", self.variant_index)
            if not os.path.isdir(path):
                path = os.path.join(self.source_path, "installers")
            files = []
            for filename in os.listdir(path):
                if filename in exclude_files:
                    continue
                filepath = os.path.join(path, filename)
                if os.path.isfile(filepath) and re.match(regex, filename):
                    files.append(filepath)
            return files
        elif self._search_mode == self.__class__.PYPI:
            raise NotImplementedError(
                "PYPI mode does not implemented in this version.")
        else:
            raise ArgumentError(f"Mode {self._search_mode} unsupported.")

    @classmethod
    def list_modes(cls):
        """List all the supported installer search modes.

        Returns:
            :obj:`list` of :obj:`int`: All supported installer search modes.
        """
        return [cls.LOCAL, cls.PYPI]

    def mode(self):
        """Return the current mode.

        Returns:
            int: The current mode.
                InstallerBuilder.LOCAL -- 0
                InstallerBuilder.PYPI -- 1
        """
        return self._search_mode

    def set_search_mode(self, mode):
        """Set search mode.

        Args:
            mode (int): The installer search mode to set.
                InstallerBuilder.LOCAL -- 0
                InstallerBuilder.PYPI -- 1

        Raises:
            ArgumentError: When the installer search mode does not support.
        """
        if mode in self.list_modes():
            self._search_mode = mode
        else:
            raise ArgumentError(f"Mode {self._search_mode} unsupported.")


class ExtractBuilder(InstallBuilder):
    """Build package from the archive file."""

    def extract(self, extract_path, installer_regex=None):
        """Extract the installers.

        Args:
            extract_path (str): The path to extract to.
            installer_regex (str): The regex to match the installer name. Only
                the matched installer will be extracted and compiled.
        """
        clear_path(extract_path)
        for installer in self.get_installers(regex=installer_regex):
            if installer.split(".")[-1] in ["gz", "xz"]:
                with tarfile.open(installer, "r") as tar:
                    tar.extractall(extract_path)
            elif installer.endswith("7z.exe"):
                name = os.path.basename(installer).split(".")[0]
                extract_path = os.path.join(extract_path, name)
                cmds = [installer, "-y", f"-o{extract_path}"]
                subprocess.run(cmds, check=True)
            elif installer.endswith(".zip"):
                with zipfile.ZipFile(installer) as zip_file:
                    zip_file.extractall(extract_path)
            else:
                suffix = installer.split(".")[-1]
                raise UnsupportedError(f"Unsupported file format: {suffix}")

    def custom_build(self, extract_path=None, installer_regex=None):
        """Run the extract build.

        Args:
            extract_path (str): The path to extract to.
            installer_regex (str): The regex to match the installer name. Only
                the matched installer will be extracted and compiled.
        """
        extract_path = extract_path or os.path.join(self.build_path, "extract")
        self.extract(extract_path, installer_regex=installer_regex)
        for name in os.listdir(extract_path):
            src = os.path.join(extract_path, name)
            dst = os.path.join(self.workspace, name)
            if os.path.isfile(src) or os.path.islink(src):
                shutil.copy2(src, dst, follow_symlinks=False)
            elif os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                # Should never be executed.
                raise UnsupportedError(f"Unsupported file format: {src}")


class CompileBuilder(ExtractBuilder):
    """Build package from source by compiler."""

    @staticmethod
    def compile(source_path, install_path, extra_config_args=None):
        """Compile the package.

        Args:
            source_path (str): The source root of this package to compile.
            install_path (str): The install path to install to.
            extra_config_args (:obj:`list` of :obj:`str`): Extra config
                arguments to pass to the configure.
        """
        extra_config_args = extra_config_args or []
        commands = [
            ["./configure", f"--prefix={install_path}"] + extra_config_args,
            ["make"],
            ["make", "install"],
        ]
        for cmds in commands:
            subprocess.run(cmds, check=True, cwd=source_path)

    def custom_build(
            self, extra_config_args=None, installer_regex=None,
            install_path=None, make_movable=False):
        """Run the compile build.

        Args:
            extra_config_args (:obj:`list` of :obj:`str`): Extra config
                arguments to pass to the configure.
            installer_regex (str): The regex to match the installer name. Only
                the matched installer will be extracted and compiled.
            install_path (str): The path to install the package. Note this is
                different with the `self.install_path`. The path will pass to
                the configure as the value of the prefix.
            make_movable (bool): Whether to make the package movable. Default
                is False.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            extract_path = os.path.join(temp_dir, "extract")
            install_path = install_path or self.workspace
            self.extract(extract_path, installer_regex=installer_regex)
            for extract in os.listdir(extract_path):
                self.compile(
                    os.path.join(extract_path, extract), install_path,
                    extra_config_args=extra_config_args)
        if make_movable:
            make_bins_movable(os.path.join(install_path, "bin"))


class MacOSBuilder(RezBuilder, abc.ABC):
    """Include some common method for build macOS package."""

    @staticmethod
    def create_open_shell(app_name, path, shell_name=""):
        """Create shell to open macOS .app file.

        Shell name is all lowercase and replace the space to underscore.

        Args:
            app_name (str): The macOS app name. Should end with `.app`.
            path (str): The directory path to put the shell to.
            shell_name (str): The shell name to Specify to.
        """
        shell_name = (shell_name or
                      app_name.lower().replace(".app", "").replace(" ", "_"))
        shell_path = os.path.join(path, shell_name)
        with open(shell_path, "w") as shell:
            shell.write(SHELL_CONTENT.format(app_name=app_name))
        mode = (stat.S_IXUSR + stat.S_IXGRP + stat.S_IXOTH + stat.S_IRUSR +
                stat.S_IRGRP + stat.S_IROTH)
        os.chmod(shell_path, mode)

    @staticmethod
    def extract_dmg(dmg_file, extract_path):
        """Extract dmg file.

        Args:
            dmg_file (str): The path of the dmg file.
            extract_path (str): The path to extract file to.
        """
        if not os.path.isdir(extract_path):
            os.makedirs(extract_path)
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                command = [
                    "hdiutil", "attach", "-nobrowse", "-mountpoint", temp_dir,
                    dmg_file
                ]
                subprocess.run(command, check=True)
                shutil.copytree(
                    temp_dir, extract_path, symlinks=True, dirs_exist_ok=True)
            finally:
                subprocess.run(["hdiutil", "detach", temp_dir], check=True)

    @staticmethod
    def extract_pkg(pkg_file, extract_path):
        """Extract pkg file.

        Will remove extract_path before extraction.

        Args:
            pkg_file (str): The path of the pkg file.
            extract_path (str): The path to extract file to.
        """
        if os.path.isdir(extract_path):
            remove_tree(extract_path)
        command = ["pkgutil", "--expand-full", pkg_file, extract_path]
        subprocess.run(command, check=True)


class MacOSDmgBuilder(MacOSBuilder, InstallBuilder):
    """Build rez package from macOS dmg installer."""

    def custom_build(self, create_shell=True, shell_name=""):
        """Install dmg file as rez package.

        Args:
            create_shell (bool): Whether to create shell to open macOS `.app`
                application. Default is True.
            shell_name (str): The shell name to Specify to.
        """
        with tempfile.TemporaryDirectory() as extract_path:
            for installer in self.get_installers():
                if installer.endswith(".dmg"):
                    self.extract_dmg(installer, extract_path)
            for file_ in os.listdir(extract_path):
                if file_.endswith(".app"):
                    src = os.path.join(extract_path, file_)
                    dst = os.path.join(self.workspace, file_)
                    shutil.copytree(src, dst)
                    if create_shell:
                        self.create_open_shell(
                            file_, self.workspace, shell_name)


class PythonBuilder(RezBuilder, abc.ABC):
    """This class include some common method for build python package."""

    def change_shebang(self, root="", shebang=""):
        """Change all the shebang of entry files where in bin directory.

        Args:
            root (str): Where the entry files placed. Default is the bin
                directory.
            shebang (str): The shebang content you want to change to.
        """
        root = root or os.path.join(self.workspace, "bin")
        if platform.system() == "Windows":
            shebang = shebang or "#!python.exe"
            make_bins_movable(root, shebang, "#!.+python.exe")
        else:
            shebang = shebang or "/usr/bin/env python"
            make_bins_movable(root, shebang)

    @staticmethod
    def install_wheel_file(wheel_file, install_path):
        """Install the wheel.

        Args:
            wheel_file (str): The path of the wheel file.
            install_path (str): Path to install
        """
        command = [
            "pip", "install", "--ignore-installed", "--no-deps",
            "--no-compile", "--target", install_path, wheel_file]
        print(f"\nInstall wheel command: {' '.join(command)}")
        subprocess.run(command, check=True)

    def to_site_packages(self, ignores=None):
        """Copy python file to site-packages directory.

        Args:
            ignores (:obj:`list` of :obj:`str`): The folder or file names
                which will be ignored when copy to site-package.
        """
        site_packages_path = os.path.join(self.workspace, "site-packages")
        if os.path.exists(site_packages_path):
            remove_tree(site_packages_path)
        os.makedirs(site_packages_path)
        if ignores is None:
            ignores = ["bin", "site-packages"]
        if "site-packages" not in ignores:
            ignores.append("site-packages")
        for filename in os.listdir(self.workspace):
            if filename not in ["bin", "site-packages"]:
                src = os.path.join(self.workspace, filename)
                shutil.move(src, site_packages_path)


class PythonSourceBuilder(PythonBuilder):
    """This class build packages from the standard python source code.

    The package structure should follow the standard python package structure.
    Reference here: https://packaging.python.org/tutorials/packaging-projects/

    """

    def create_wheel(self, is_venv=True):
        """Create wheel file from source code and put into a temp dir.

        Args:
            is_venv (bool): Whether to create venv when build python package.

        Returns:
            str: The wheel file path.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_src = os.path.join(temp_dir, "src")
            shutil.copytree(self.source_path, temp_src)
            wheel_dir = os.path.join(self.build_path, "wheel_dir")
            command = ["pyproject-build", "-o", wheel_dir]
            if not is_venv:
                command.append("--no-isolation")
                env = dict(os.environ)
            else:
                env = self.get_no_pip_environment()
            print(f"\nWheel create command: {' '.join(command)}")
            # Remove pip from environment to let venv install it.
            subprocess.run(command, check=True, cwd=temp_src, env=env)
        wheel_file_name = [
            name for name in os.listdir(wheel_dir) if name.endswith(".whl")][0]
        return os.path.join(wheel_dir, wheel_file_name)

    def custom_build(self, is_change_shebang=False, is_venv=True, shebang=""):
        """Build package from source.

        Args:
            is_change_shebang (bool): Whether to change the shebang from the
                bin files.
            is_venv (bool): Whether to create venv when build python package.
            shebang (str): The shebang content you want to change to.
        """
        wheel_filepath = self.create_wheel(is_venv=is_venv)
        self.install_wheel_file(wheel_filepath, self.workspace)
        self.to_site_packages()
        if is_change_shebang:
            self.change_shebang(shebang=shebang)

    @staticmethod
    def get_no_pip_environment():
        """Remove pip path from the PYTHONPATH environment variables."""
        env = dict(os.environ)
        delimiter = get_delimiter()
        env["PYTHONPATH"] = delimiter.join([
            path for path in env["PYTHONPATH"].split(delimiter)
            if not path.startswith(os.environ[f"REZ_PIP_ROOT"])
        ])
        return env


class PythonWheelBuilder(PythonBuilder, InstallBuilder):
    """Build the external package from python wheel file."""

    def custom_build(self, is_change_shebang=False, shebang=""):
        """Build package from wheel file.

        Args:
            is_change_shebang (bool): Whether to change shebang from bin
                directory.
            shebang (str): The shebang content you want to change to.
        """
        wheels = [wheel for wheel in self.get_installers()
                  if wheel.endswith(".whl")]
        # Python installer always only one whl file.
        self.install_wheel_file(wheels[0], self.workspace)
        self.to_site_packages()
        if is_change_shebang:
            self.change_shebang(shebang=shebang)

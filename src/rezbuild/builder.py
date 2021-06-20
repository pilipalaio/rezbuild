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
import shutil
import subprocess
import tempfile

# Import local modules
from rezbuild.utils import remove_tree
from rezbuild.exceptions import ArgumentError


class RezBuilder(abc.ABC):
    """The basic class of RezBuild."""

    def __init__(self, **kwargs):
        """Initialize builder."""
        self.build_path = os.environ["REZ_BUILD_PATH"]
        self.install_path = os.environ["REZ_BUILD_INSTALL_PATH"]
        self.project_name = os.environ["REZ_BUILD_PROJECT_NAME"]
        self.project_version = os.environ["REZ_BUILD_PROJECT_VERSION"]
        self.source_path = os.environ["REZ_BUILD_SOURCE_PATH"]
        self.variant_index = os.environ["REZ_BUILD_VARIANT_INDEX"]
        self.workspace = os.path.join(self.build_path, "workspace")
        # self.temp_dirs list all the temporary directory objects that create
        # by tempfile.
        self.temp_dirs = []
        super().__init__(**kwargs)

    def build(self):
        """Build the package."""
        self.create_work_dir()
        self.custom_build()
        self.install()
        self.clean_temp_dir()

    def clean_temp_dir(self):
        """Clean all the temp dir."""
        for temp_dir in self.temp_dirs:
            temp_dir.cleanup()

    def custom_build(self):
        """Execute custom build method.

        Raises:
            NotImplementedError: When this method does not implemented by the
                child class.
        """
        raise NotImplementedError(
            "This method does not implemented by the invoker.")

    def create_work_dir(self):
        """Create the work directory.

        If the work directory already exists, remove the old one and create it.
        """
        if os.path.exists(self.workspace):
            remove_tree(self.workspace)
        os.makedirs(self.workspace)

    def install(self):
        """Copy files from work directory to self.install_path."""
        if os.environ.get("REZ_BUILD_INSTALL") == "1":
            if os.path.exists(self.install_path):
                remove_tree(self.install_path)
            shutil.copytree(self.workspace, self.install_path)


class InstallBuilder(RezBuilder, abc.ABC):
    """This class is the base builder to build package from installer."""

    # Class constants to mark up where the installers come from. Default is
    # LOCAL.
    LOCAL = 0
    PYPI = 1

    def __init__(self, mode=None, **kwargs):
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

    def get_installers(self, local_path=None):
        """Get installers.

        In `InstallerBuilder.LOCAL` mode, the default place is a folder named
        "rez_installers" under the source root. Each variants has a folder
        named with its "REZ_BUILD_VARIANT_INDEX" under the installers
        directory. The directory structure should looks like this:

        source_root/
            |___rez_installers/
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

        Returns:
            :obj:`list` of :obj:`str`: All the paths of the installers.

        Raises:
            ArgumentError: When the installer search mode does not support.
        """
        if self._search_mode == self.__class__.LOCAL:
            if local_path:
                path = os.path.join(local_path, self.variant_index)
                if os.path.isfile(path):
                    return path
            else:
                path = os.path.join(
                    self.source_path, "rez_installers", self.variant_index)
            return [os.path.join(path, file_) for file_ in os.listdir(path)]
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


class PythonBuilder(RezBuilder, abc.ABC):
    """This class include some common method for build python package."""

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

    def create_wheel(self):
        """Create wheel file from source code and put into a temp dir.

        Returns:
            str: The wheel file path.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_src = os.path.join(temp_dir, "src")
            shutil.copytree(self.source_path, temp_src)
            wheel_dir = os.path.join(self.build_path, "wheel_dir")
            command = ["pyproject-build", "-o", wheel_dir]
            print(f"\nWheel create command: {' '.join(command)}")
            subprocess.run(command, check=True, cwd=temp_src)
        wheel_file_name = [
            name for name in os.listdir(wheel_dir) if name.endswith(".whl")][0]
        return os.path.join(wheel_dir, wheel_file_name)

    def custom_build(self):
        """Build package from source."""
        wheel_filepath = self.create_wheel()
        self.install_wheel_file(wheel_filepath, self.workspace)
        self.to_site_packages()


class PythonWheelBuilder(PythonBuilder, InstallBuilder):
    """Build the external package from python wheel file."""

    def custom_build(self):
        """Build package from wheel file."""
        wheels = [wheel for wheel in self.get_installers()
                  if wheel.endswith(".whl")]
        # Python installer always only one whl file.
        self.install_wheel_file(wheels[0], self.workspace)
        self.to_site_packages()

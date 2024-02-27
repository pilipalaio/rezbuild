Change log of rezbuild
======================

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Version 0.16.0 (February, 27th, 2024)
-------------------------------------
Added:
  - `PythonWheelBuilder.custom_build` add new parameter `wheel_install_path`.

Changed:
  - Use `python -m pip` instead of `pip`.

Version 0.15.1 (June, 8th, 2022)
--------------------------------
Changed:
- Add more documents.

Version 0.15.0 (June, 7th, 2022)
--------------------------------
Added:
  - `MsiInstaller`.
  - `WindowsInstaller`.

Changed:
  - Add more documents.
  - Improve docstring.
  - `InstallBuilder.mode` to `InstallBuilder.get_mode`.

Removed:
  - `PythonBuilder.to_site_packages`.

Version 0.14.1 (May, 8th, 2022)
-------------------------------
Added:
  - Add `CopyBuilder` to `rezbuild.__init__`.

Version 0.14.0 (May, 8th, 2022)
-------------------------------
Added:
  - `CopyBuilder`.

Version 0.13.1 (May, 7th, 2022)
-------------------------------
Fixed:
  Remake temp directory after remove it manually.

Version 0.13.0 (May, 5th, 2022)
-------------------------------
Added:
  - `rezbuild.log` module.
  - clean the wheel directory before create wheel file.

Changed:
  - Rename `rezbuild.constant` to `rezbuild.constants`.

Fixed:
  - Raise InstallerNotFoundError when can't find any installers.
  - Skip the ReNotMatchError and print an error.
  - Support gui_scripts in PythonBuilder.

Removed:
  - Remove `to_site_packages` function, package will put in the installation
      directory.
  - remove `RezBuilder.temp_dirs`.

Version 0.12.1 (April, 5th, 2022)
---------------------------------
Fixed:
  - Remove assignment expression.

Version 0.12.0 (April, 4th, 2022)
---------------------------------
Changed:
  - Make the installation docs clearly.
  - Python requirement back to python-3.6.
  - Stop auto get the version number. 

Version 0.11.0 (January 4th, 2022)
----------------------------------
Added:
  - `PythonBuilder.install_wheel` method.
  - `PythonSourceBuilder.create_wheel` add parameter `source_root`.

Changed:
  - All the parameter named `is_venv` to `use_venv`.
  - All the parameter named `is_change_shebang` to `change_shebang`.
  - `PythonBuilder.install_file_by_pip` to 
    `PythonBuilder.install_wheel_by_pip`.
  - Use wheel file to install python source archive file.   

Version 0.10.2 (December 31st, 2021)
------------------------------------
Fixed:
  - convert bytes twice bug (#12)

Version 0.10.1 (December 31st, 2021)
------------------------------------
Added:
  - `ReNotMatchError`.
Fixed:
  - Change binary shebang bug (#11)

Version 0.10.0 (December 22th, 2021)
------------------------------------
Added:
  - `PythonSourceArchiveBuilder`.
Changed:
  - Function `PythonBuilder.install_wheel_file` to
    `PythonBuilder.install_file_by_pip`

Version 0.9.1 (November 12th, 2021)
-----------------------------------
Changed:
  - Update requires in `package.py`.

Fixed:
  - `ExtractBuilder` do not copy directory bug.
  - `ExtractBuilder` can not copy file from the extract_path to workspace.

Version 0.9.0 (November 10th, 2021)
-----------------------------------
Added:
  - `shell_name` parameter into `MacOSDmgBuilder`.
  - `MacOSBuilder` into `__all__`.
  - Function `bin_utils.make_bin_movable`.
  - Method `bin_utils.MachO.parse_arch`.
  - Parameter `extra_lib_dirs` into `bin_utils.make_bins_movable`.
  - Parameter `extra_lib_dirs` into `bin_utils.MachO.make_macho_movable`.

Changed:
  - Remove parameter `rpath` from `bin_utils.make_bins_movable`.
  - Remove parameter `rpath` from `bin_utils.MACHO.make_macho_movable`.

Fixed:
  - Get empty relative path bug in `utils.get_relative_path`.

Removed:
  - Method `bin_utils.MACHO.parse_load_command`.

Version 0.8.0 (October 22nd, 2021)
----------------------------------
Added:
  - Support custom shebang content in `PythonWheelBuilder` and
    `PythonSourceBuilder`.

Version 0.7.0 (October 11th, 2021)
----------------------------------
Added:
  - Support zip file in `ExtractBuilder`.
  - `MacOSDmgBuilder` to support macOS DMG file.

Version 0.6.0 (August 26th, 2021)
---------------------------------
Added:
  - `install_requires` into `setup.cfg`.
  - `bin_utils` module.
  - `utils.clear_path` function.
  - `utils.get_relative_path` function.

Changed:
  - Move bin relative function into `bin_utils` module.
  - Support make bin movable on `CompileBuilder`.

Version 0.5.1 (August 18th, 2021)
---------------------------------
Fixed:
  - Remove other path when create no pip environment.(#1)

Version 0.5.0 (August 12th, 2021)
--------------------------------
Added:
  - `ExtractBuilder`.
  - `CompileBuilder`.
  - `utils.make_bins_movable` function.

Changed:
  - Support get installers from `installers` folder.
  - Add `regex` parameter in `InstallBuilder.get_installers`.
  - Changed python requires to 3.8+.
  - Rename `PythonBuilder.change_shebangs` to `PythonBuilder.change_shebang`.
  - Rename `RezBuilder.project_name` to `RezBuilder.name`.
  - Rename `RezBuilder.project_version` to `RezBuilder.version`.

Version 0.4.0 (July 31st, 2021)
-------------------------------
Added:
  - `utils.get_windows_shebang` function.

Changed:
  - Support change windows shebang.
  - Support create wheel without venv.

Version 0.3.0 (July 29th, 2021)
-------------------------------
Added:
  - Add is_change_shabang options into
    `rezbuild.PythonSourceBuilder.custom_build`.

Changed:
  - Update chinese documents.

Version 0.2.0 (July 27th, 2021)
-------------------------------
Added:
  - Add change_shabang function in `rezbuild.utils`.
  - Add is_change_shabang options into
    `rezbuild.PythonWheelBuilder.custom_build`.
  - Add content of README.md file.
  - Add README_zh_CN.md file.
  - Add forgotten change log of version 0.1.1.

Fixed:
  - Do not install pip in venv bug.

Version 0.1.1 (June 22nd, 2021)
-------------------------------
Fixed:
  - Add the missing dependency package `pip`.

Version 0.1.0 (June 20th, 2021)
-------------------------------
Added:
   - Initial version

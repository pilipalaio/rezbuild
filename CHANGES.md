Change log of rezbuild
======================

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Version 0.7.0 (October 11th, 2021)
----------------------------------
Added:
  - Support zip file in `ExtractBuilder`.
  - Support macOS DMG file.

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

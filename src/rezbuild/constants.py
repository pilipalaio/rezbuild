"""Constants."""

PACKAGE_NAME = "rezbuild"

SHELL_CONTENT = """#!/bin/bash

pwd=$( cd $( dirname $0 ) && pwd )
path="$pwd/{app_name}"
open -a "$path"
"""

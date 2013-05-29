#!/usr/bin/env python

from distutils.core import setup
import subprocess

CMAKE_NOT_INSTALLED = "cmake not found in PATH!"
FAILURE_IN_COMPILING_PHANTOMPY = "failed to compile phantompy!"
UNABLE_TO_GET_PHANTOMPY_SOURCE = "Unable to download phantompy source code!"

PHANTOMPY_REPO = "git://github.com/niwibe/phantompy.git"

def get_git_path():
    pass

def download_phantompy_source():
    pass

def get_cmake_path():
    pass


def compile_phantompy():
    pass


def capabilities():
    return {'git':get_git_path(), }

setup(name='PhantomFFIPy',
      version='0.0',
      description='FFI interface for phantompy',
      author='Ben Jolitz',
      requires=['cffi'],
      author_email='ben.jolitz@gmail.com',
      url='https://github.com/benjolitz/phantomffipy',
      packages=['phantomffipy'])

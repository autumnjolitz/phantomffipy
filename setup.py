#!/usr/bin/env python

from distutils.core import setup
from distutils import log
from distutils.spawn import find_executable
import subprocess
import shlex
import os.path

CMAKE_NOT_INSTALLED = "cmake not found in PATH!"
FAILURE_IN_COMPILING_PHANTOMPY = "failed to compile phantompy!"
UNABLE_TO_GET_PHANTOMPY_SOURCE = "Unable to download phantompy source code!"
ERROR_IN_GIT_CLONE = "Failed to clone git repository!\n{0}"

GIT_PULL_FAILED = "Failed to update local git copy. Using " + \
    "old/potentially empty repo!"

SUBPROCESS_ERROR = "subprocess.Popen threw an exception! " + \
    "Location {2}, Command: {1}, Exception message: {0}"

PHANTOMPY_REPO = "git://github.com/niwibe/phantompy.git"
PHANTOMPY_REPO_ZIP = "https://github.com/niwibe/phantompy/archive/master.zip"
CLONE_REPO = "{git} clone {repo} {path}"
PHANTOMPY_SRC_DIR = "src/phantompy"
UPDATE_LOCAL_COPY = "{git} pull origin master"
SUBPROCESS_KWARGS = {
    'stdout': subprocess.PIPE,
    'stderr': subprocess.PIPE,
    'cwd': os.path.dirname(os.path.abspath(__file__))
}


def download_git(opts):
    if opts['git']:
        try:
            subprocess.call([opts['git']])
        except OSError:
            log.debug("{0} not a valid command!".format(opts['git']))
            return None
        else:
            git_src_dir = os.path.join(
                SUBPROCESS_KWARGS['cwd'], PHANTOMPY_SRC_DIR)
            if not os.path.exists(PHANTOMPY_SRC_DIR):
                command = CLONE_REPO.format(
                    repo=PHANTOMPY_REPO,
                    path=git_src_dir,
                    git=opts['git'])
                try:
                    stdout, stderr = subprocess.Popen(
                        shlex.split(command),
                        **SUBPROCESS_KWARGS).communicate()
                except OSError as e:
                    log.debug(SUBPROCESS_ERROR.format(
                        str(e), command, SUBPROCESS_KWARGS['cwd']))
                else:
                    if stderr:
                        log.debug(ERROR_IN_GIT_CLONE.format(stderr))
                        return None
            else:
                command = UPDATE_LOCAL_COPY.format(opts['git'])
                try:
                    stdout, stderr = subprocess.Popen(
                        shlex.split(command),
                        dict(SUBPROCESS_KWARGS,
                             **{'cwd': git_src_dir}))
                except OSError as e:
                    log.debug(SUBPROCESS_ERROR.format(
                        str(e), command, git_src_dir))
                if stderr:
                    log.debug(GIT_PULL_FAILED)
            return git_src_dir
    return None


def download_url(opts):
    return None


def download_phantompy_source(opts):
    for method in (download_git, download_url,):
        result = method(opts)
        if result is not None:
            break
    else:
        raise Exception("Failed to download phantompy source code!")
    return result


def get_cmake_path():
    path = find_executable('cmake')
    if not path:
        raise CMAKE_NOT_INSTALLED
    return path


def compile_phantompy():
    pass


def capabilities():
    return {'git': find_executable('git'), 'cmake': get_cmake_path()}

setup(name='PhantomFFIPy',
      version='0.0',
      description='FFI interface for phantompy',
      author='Ben Jolitz',
      requires=['cffi'],
      author_email='ben.jolitz@gmail.com',
      url='https://github.com/benjolitz/phantomffipy',
      packages=['phantomffipy'])

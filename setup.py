#!/usr/bin/env python
from distutils.core import setup
import distutils.command.build
import distutils.command.clean
from distutils import log
from distutils.spawn import find_executable
import subprocess
import shutil
import shlex
import os.path
import glob
from urllib import urlopen
import zipfile
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

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
PHANTOMPY_SRC_DIR = os.path.join("src", "phantompy")
UPDATE_LOCAL_COPY = "{git} pull origin master"
SUBPROCESS_KWARGS = {
    'stdout': subprocess.PIPE,
    'stderr': subprocess.PIPE,
    'cwd': os.path.dirname(os.path.abspath(__file__))
}


def download_git(opts):
    if opts['git']:
        try:
            stdout, stderr = subprocess.Popen([opts['git']], **SUBPROCESS_KWARGS).communicate()
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
    src_dir = os.path.join(SUBPROCESS_KWARGS['cwd'], 'src')
    dest_dir = os.path.join(src_dir, 'phantompy')
    zipfilename = os.path.join(src_dir, 'phantompy-master.zip')
    for downloader in ('wget', 'fetch', 'curl',):
        if find_executable(downloader):
            break
    else:
        downloader = None
        buf = StringIO.StringIO()
        try:
            data = urlopen(PHANTOMPY_REPO_ZIP)
        except:
            raise Exception(UNABLE_TO_GET_PHANTOMPY_SOURCE)
        else:
            buf.write(data.read())
            data.close()
            buf.seek(0)
        if downloader:
            try:
                subprocess.call(
                    shlex.split("{0} {1}".format(
                        downloader, PHANTOMPY_REPO_ZIP)),
                    cwd=src_dir)
            except OSError:
                log.debug("Failed Command:\n{0} {1}".format(
                    downloader, PHANTOMPY_REPO_ZIP))
                return None

        archive = zipfile.ZipFile(
            buf or zipfilename)
        archive.extractall(
            path=os.path.join(SUBPROCESS_KWARGS['cwd'], 'src'))
        os.rename(
            os.path.join(
                SUBPROCESS_KWARGS['cwd'], 'src', 'phantompy-master'),
            dest_dir)
        if not buf:
            os.remove(zipfilename)
        return dest_dir
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


def compile_phantompy(opts):
    if not os.path.exists(opts['phantompy_src']):
        opts['phantompy_src'] = download_phantompy_source(opts)
    retval = subprocess.call(shlex.split('cmake ..'),
                             cwd=os.path.join(opts['phantompy_src'], 'build'))
    if retval:
        raise Exception("CMake Error!")
    retval = subprocess.call(shlex.split('make'),
                             cwd=os.path.join(opts['phantompy_src'], 'build'))
    if retval:
        raise Exception("Make error!")


def get_paths():
    return {'git': find_executable('git'), 'cmake': get_cmake_path(),
            'new_module_dir': os.path.join(
                SUBPROCESS_KWARGS['cwd'], 'build', 'lib',
                'phantomffipy'),
            'phantompy_src': os.path.join(
                SUBPROCESS_KWARGS['cwd'], 'src', 'phantompy')}


class build(distutils.command.build.build):
    def run(self):
        result = distutils.command.build.build.run(self)
        print("building _phantompy.so")
        opts = get_paths()
        compile_phantompy(opts)
        for fileish in glob.glob(os.path.join(
                opts['phantompy_src'], 'build', '_phantompy*.so*')):
            if os.path.isfile(fileish) and not os.path.islink(fileish):
                print("installing {0} -> {1}".format(
                    fileish, os.path.join(opts['new_module_dir'],
                                          '_phantompy.so')))
                shutil.move(fileish, os.path.join(
                    opts['new_module_dir'], '_phantompy.so'))
                break
        else:
            raise Exception("Library not found!")
        headers = (os.path.join(opts['phantompy_src'], 'lib', 'phantompy.hpp'),
                   os.path.join(opts['new_module_dir'], 'phantompy.hpp'),)
        print("installing {0} -> {1}".format(*headers))
        shutil.copy(*headers)
        return result


class clean(distutils.command.clean.clean):
    def run(self):
        phantompy_dir = os.path.join(
            SUBPROCESS_KWARGS['cwd'], 'src', 'phantompy')
        if os.path.exists(phantompy_dir):
            shutil.rmtree(phantompy_dir)
        return distutils.command.clean.clean.run(self)


setup(name='PhantomFFIPy',
      version='0.0',
      description='FFI interface for phantompy',
      author='Autumn Jolitz',
      requires=['cffi'],
      author_email='autumn.jolitz@gmail.com',
      url='https://github.com/autumnjolitz/phantomffipy',
      cmdclass={
          'build': build,
          'clean': clean
      },
      packages=['phantomffipy'],
      )

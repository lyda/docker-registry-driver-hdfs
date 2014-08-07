# -*- coding: utf-8 -*-
# Copyright (c) 2014 Insight Centre.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
docker_registry.drivers.hdfs
~~~~~~~~~~~~~~~~~~~~~~~~~~

This is a hadoop based hdfs driver.  It would be better to do this
with snakebite (https://github.com/spotify/snakebite) but it doesn't
yet support writing to hdfs.

"""

import os
import hadoopy
import shutil
from hadoopy._hdfs import _checked_hadoop_fs_command

from ..core import driver
from ..core import exceptions
from ..core import lru

# Hadoopy fs functions are... deficient.  Yes this is gross.  I'm sorry.


def hdfs_mkdirp(path):
    cmd = "hadoop fs -mkdir -p %s" % (path)
    rcode, stdout, stderr = _checked_hadoop_fs_command(cmd)


def hdfs_du(path):
    cmd = "hadoop fs -du -s %s" % (path)
    rcode, stdout, stderr = _checked_hadoop_fs_command(cmd)
    if stdout:
        return stdout.split(' ')[0]


def hdfs_rmr(path):
    cmd = "hadoop fs -rm -r %s" % (path)
    rcode, stdout, stderr = _checked_hadoop_fs_command(cmd)


def hdfs_putf(local_path, hdfs_path):
    cmd = "hadoop fs -put -f %s %s" % (local_path, hdfs_path)
    rcode, stdout, stderr = _checked_hadoop_fs_command(cmd)


class Storage(driver.Base):

    supports_bytes_range = True

    def __init__(self, path=None, config=None):
        self._config = config
        self._root_path = path or '/registry'
        self._local_path = getattr(self._config, 'local_path')

    def _init_path(self, path=None):
        if path:
            hdfs_path = os.path.join(self._root_path, path)
        else:
            hdfs_path = self._root_path
        local_path = os.path.join(self._local_path, path)
        return local_path, hdfs_path

    def _create_local(self, local_path):
        dirname = os.path.dirname(local_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def _create_hdfs(self, hdfs_path):
        dirname = os.path.dirname(hdfs_path)
        if not hadoopy.exists(dirname):
            hdfs_mkdirp(dirname)

    @lru.get
    def get_content(self, path):
        local_path, hdfs_path = self._init_path(path)
        self._create_local(local_path)
        try:
            if not os.path.exists(local_path):
                    hadoopy.get(hdfs_path, local_path)
            with open(local_path, mode='rb') as f:
                d = f.read()
        except Exception as e:
            raise exceptions.FileNotFoundError('%s is not there (%s)'
                                               % (local_path, e.strerror))

        return d

    @lru.set
    def put_content(self, path, content):
        local_path, hdfs_path = self._init_path(path)
        self._create_local(local_path)
        with open(local_path, mode='wb') as f:
            f.write(content)
        self._create_hdfs(hdfs_path)
        hdfs_putf(local_path, hdfs_path)
        return hdfs_path

    def stream_read(self, path, bytes_range=None):
        local_path, hdfs_path = self._init_path(path)
        self._create_local(local_path)
        nb_bytes = 0
        total_size = 0
        if not os.path.exists(local_path):
            self._create_local(local_path)
            hadoopy.get(hdfs_path, local_path)
        try:
            with open(local_path, mode='rb') as f:
                if bytes_range:
                    f.seek(bytes_range[0])
                    total_size = bytes_range[1] - bytes_range[0] + 1
                while True:
                    buf = None
                    if bytes_range:
                        # Bytes Range is enabled
                        buf_size = self.buffer_size
                        if nb_bytes + buf_size > total_size:
                            # We make sure we don't read out of the range
                            buf_size = total_size - nb_bytes
                        if buf_size > 0:
                            buf = f.read(buf_size)
                            nb_bytes += len(buf)
                        else:
                            # We're at the end of the range
                            buf = ''
                    else:
                        buf = f.read(self.buffer_size)
                    if not buf:
                        break
                    yield buf
        except IOError:
            raise exceptions.FileNotFoundError('%s is not there' % path)

    def stream_write(self, path, fp):
        # Size is mandatory
        local_path, hdfs_path = self._init_path(path)
        self._create_local(local_path)
        with open(local_path, mode='wb') as f:
            try:
                while True:
                    buf = fp.read(self.buffer_size)
                    if not buf:
                        break
                    f.write(buf)
            except IOError:
                pass
        self._create_hdfs(hdfs_path)
        hdfs_putf(local_path, hdfs_path)

    def list_directory(self, path=None):
        prefix = ''
        if path:
            prefix = '%s/' % path
        local_path, hdfs_path = self._init_path(path)
        exists = False
        try:
            for d in hadoopy.ls(hdfs_path):
                exists = True
                yield os.path.relpath(d, self._local_path)
        except Exception:
            pass
        if not exists:
            raise exceptions.FileNotFoundError('%s is not there' % path)

    def exists(self, path):
        local_path, hdfs_path = self._init_path(path)
        if os.path.exists(local_path):
            return True
        else:
            return hadoopy.exists(hdfs_path)

    @lru.remove
    def remove(self, path):
        local_path, hdfs_path = self._init_path(path)
        if os.path.isdir(local_path):
            shutil.rmtree(local_path)
            return
        try:
            os.remove(local_path)
        except Exception:
            pass
        try:
            hdfs_rmr(hdfs_path)
        except Exception:
            raise exceptions.FileNotFoundError('%s is not there' % path)

    def get_size(self, path):
        local_path, hdfs_path = self._init_path(path)
        try:
            return os.path.getsize(local_path)
        except OSError:
            try:
                return hdfs_du(hdfs_path)
            except Exception:
                raise exceptions.FileNotFoundError('%s is not there' % path)

#
# Editor modelines  -  http://www.wireshark.org/tools/modelines.html
#
# Local variables:
# c-basic-offset: 4
# tab-width: 8
# indent-tabs-mode: nil
# End:
#
# vi: set shiftwidth=4 tabstop=8 expandtab:
# :indentSize=4:tabSize=8:noTabs=true:
#

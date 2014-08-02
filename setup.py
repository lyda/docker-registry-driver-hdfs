#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import setuptools
except ImportError:
    import distutils.core as setuptools

setuptools.setup(
    name='docker-registry-driver-hdfs',
    version='0.0.1',
    author='Kevin Lyda',
    author_email='kevin@ie.suberic.net',
    maintainer='Kevin Lyda',
    maintainer_email='kevin@ie.suberic.net',
    url='https://github.com/lyda/docker-registry-driver-hdfs',
    description='Docker registry HDFS driver',
    long_description=open('./README.md').read(),
    download_url='https://github.com/lyda/docker-registry-driver-hdfs/archive/master.zip',
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'Programming Language :: Python',
                 # 'Programming Language :: Python :: 2.6',
                 'Programming Language :: Python :: 2.7',
                 # 'Programming Language :: Python :: 3.2',
                 # 'Programming Language :: Python :: 3.3',
                 # 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: Implementation :: CPython',
                 'Operating System :: OS Independent',
                 'Topic :: Utilities',
                 'License :: OSI Approved :: Apache Software License'],
    platforms=['Independent'],
    license=open('./LICENSE').read(),
    namespace_packages=['docker_registry', 'docker_registry.drivers'],
    packages=['docker_registry', 'docker_registry.drivers'],
    install_requires=open('./requirements.txt').read(),
    zip_safe=False,
    tests_require=open('./tests/requirements.txt').read(),
    test_suite='nose.collector'
)

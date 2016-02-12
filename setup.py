#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import ast

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def extract_version():
    with open('qqqfome/__init__.py', 'rb') as f_version:
        ast_tree = re.search(
            r'__version__ = (.*)',
            f_version.read().decode('utf-8')
        ).group(1)
        if ast_tree is None:
            raise RuntimeError('Cannot find version information')
        return str(ast.literal_eval(ast_tree))


packages = ['qqqfome', 'qqqfome.test']
package_data = {'qqqfome': ['config.json']}

version = extract_version()

long_description = ''

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='qqqfome',
    version=version,
    keywords=['internet', 'daemon', 'sqlite'],
    description='I\'m a daemon server that '
                'auto send message to your zhihu new followers.',
    long_description=long_description,
    author='7sDream',
    author_email='didislover@gmail.com',
    license='MIT',
    url='https://github.com/7sDream/qqqfome',

    install_requires=[
        'zhihu-py3', 
    ],
    
    packages=packages,
    package_data=package_data,

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: No Input/Output (Daemon)',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Database', 
        'Topic :: Internet :: WWW/HTTP'
    ],

    entry_points={
        'console_scripts': [
            'qqqfome = qqqfome.entry:main'
        ]
    }
)

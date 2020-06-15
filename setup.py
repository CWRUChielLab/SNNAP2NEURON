# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.md', 'r') as f:
    README = f.read()

setup(
    name = 'snnap2neuron',
    version = '0.1.0',
    description = 'An automated translation tool for converting SNNAP models into NEURON models',
    packages = ['snnap2neuron'],
    install_requires = [],
    entry_points = {'console_scripts': ['snnap2neuron=snnap2neuron.scripts:main']},
    long_description = README,
    keywords = ['neuroscience', 'modeling', 'model', 'SNNAP', 'NEURON'],
    # author = 'Jeffrey Gill',
    # author_email = 'jeffrey.p.gill@gmail.com',
    license = 'GPLv3',
    url = 'https://github.com/CWRUChielLab/SNNAP2NEURON',
    project_urls = {
        'Source code': 'https://github.com/CWRUChielLab/SNNAP2NEURON',
        'Bug tracker': 'https://github.com/CWRUChielLab/SNNAP2NEURON/issues',
    },
    classifiers = [
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
)

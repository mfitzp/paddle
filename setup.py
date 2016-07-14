#!/usr/bin/env python
# coding=utf-8
import os, sys
from setuptools import setup, find_packages

setup(

    name='Paddle',
    version='0.5',
    author='Martin Fitzpatrick',
    author_email='martin.fitzpatrick@gmail.com',
    url='https://github.com/mfitzp/paddle',
    download_url='https://github.com/mfitzp/paddle/zipball/master',
    description='MaxQuant quantified data processing tool, outputting PaDuA format files.',
    long_description='MaxQuant quantified data processing tool, outputting PaDuA format files',
        
    packages = find_packages(),
    include_package_data = True,
    package_data = {
        '': ['*.txt', '*.rst', '*.md'],
        'plugins':['*'],
    },
    include_files= [
        ('VERSION','VERSION'),
        ('paddle/static', 'static'),
        ('paddle/tools', 'tools'),
        ('paddle/translations', 'translations'),
        ('paddle/icons', 'icons'),
        ],
    
    exclude_package_data = { '': ['README.txt'] },
    entry_points={
        'gui_scripts': [
            'Paddle = paddle.paddle:main',
        ]
    },

    install_requires = [
            'PyQt5',
            'sip',
            'numpy>=1.5.0',
            'scipy>=0.14.0',
            'pyqtconfig',
            'matplotlib',
            'padua',
            ],


    keywords='bioinformatics data analysis proteomics research science',
    license='GPL',
    classifiers=['Development Status :: 3 - Alpha',
               'Natural Language :: English',
               'Operating System :: OS Independent',
               'Programming Language :: Python :: 2',
               'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
               'Topic :: Scientific/Engineering :: Bio-Informatics',
               'Topic :: Education',
               'Intended Audience :: Science/Research',
               'Intended Audience :: Education',
              ],

    )
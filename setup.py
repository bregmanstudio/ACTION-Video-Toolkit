#!/usr/bin/env python
import glob

from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib'] 

setup(name='Action',
      version='0.12-11-01',
      description='Action Cinematic Information Retrieval Python Toolkit',
      long_description="""This package provides tools for reading, analyzing, manipulating, storing, retrieving, viewing, and evaluating, information processing operations on video files.""",

      author='Thomas Stoll',      
      author_email='thomas.m.stoll [AT] dartmouth [DOT] edu',
      url='http://bregman.dartmouth.edu/~action',
      license='GPL v. 2.0 or higher',
      platforms=['OS X (any)', 'Linux (any)', 'Windows (any)'],
      packages=['action'],
      #data_files=[('action/audio/', glob.glob('action/audio/*.wav')),
      #            ('action/video/', glob.glob('action/video/*.mov')),
      #            ('action/examples/', glob.glob('action/examples/*.py'))]
     )

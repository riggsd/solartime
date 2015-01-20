# Copyright 2015, David Riggs <driggs@myotisoft.com>
# Copyright 2009-2014, Simon Kennedy <sffjunkie+code@gmail.com>

import io
import sys
import os.path
from setuptools import setup

import solartime


def read(*names, **kwargs):
    return io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")
    ).read()

        
setup(name='solartime',
      version=solartime.__version__,
      description='Calculations for solar time such as dawn, sunrise, sunset, dusk.',
      long_description=read('README'),
      author='David Riggs',
      author_email='driggs@myotisoft.com',
      url='',
      license='Apache-2.0',
      py_modules=['solartime'],
      install_requires=['pytz'],
      classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
      ],
)

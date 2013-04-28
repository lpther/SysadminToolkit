from distribute_setup import use_setuptools
use_setuptools()

from setuptools import *


setup(
    name='SysadminToolkit',
    version='0.1.0',
    author='Louis-Philippe Theriault',
    author_email='lpther@gmail.com',
    packages=find_packages('./sysadmintoolkit'),
    package_dir={'sysadmintoolkit':'./sysadmintoolkit', 'builtinplugins':'./sysadmintoolkit/builtinplugins'},
    url='https://github.com/lpther/SysadminToolkit',
    license='See LICENSE.txt',
    description='',
    long_description=open('README.txt').read(),
    test_suite="tests",
)

# coding: utf-8
"""
ADMS
-----

ADMS is just a advertisement of manager service

"""
 
import re
import ast 
import os
import os.path
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup 
 
 
_version_re = re.compile(r'__version__\s+=\s+(.*)')
 
# securely read version info
with open('adms/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

data_dir = 'adms/res'
data = [os.path.join(data_dir, f) for f in os.listdir(data_dir)]
 
setup(
    name='adms',
    version=version,
    url='http://git.adleida.com/adms/',
    author='adleida',
    author_email='noreply@adleida.com',
    description='a advertisement of manager service',
    long_description=__doc__,
    packages=['adms', 'adms.ext'],
    package_data={'adms': data},
    include_package_data=True,
    zip_safe=False,
    platforms='linux2',
    entry_points='''
        [console_scripts]
        adms=adms.cli:main
    ''',
    install_requires=[
        'Flask==0.10.1',
        'Flask-RESTful==0.3.2',
        'pyyaml==3.11',
        'pymongo==2.8',
        # 'redis==2.10.3',
        'jsonschema==2.4.0',
        'requests==2.6.0',
        'toolz==0.7.1',
        # 'pillow==2.7.0',
        'ipdb==0.8',
    ],  
)

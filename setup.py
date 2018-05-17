import re
from os import path
from setuptools import setup, find_packages

requirments = ['Flask>=0.1', 'requests>=2.0']

version_file = path.join(
    path.dirname(__file__), 'flask_proxy', '__version__.py')
with open(version_file, 'r') as fp:
    m = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", fp.read(), re.M)
    version = m.groups(1)[0]

setup(
    name='Flask-Proxy',
    version=version,
    license='BSD',
    author='mecforlove',
    author_email='mecforlove@outlook.com',
    description='',
    packages=find_packages(exclude=['tests']),
    classifiers=[
        'Framework :: Flask',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
    ],
    install_requires=requirments)

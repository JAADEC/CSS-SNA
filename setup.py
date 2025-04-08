from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
   name='css-sna',
   version='1.0',
   description='Social Network Analysis code',
   license="MIT",
   long_description=long_description,
   author='Walker Haskins, Jaap Dechering',
   author_email='foomail@foo.example',
   packages=['css-sna'],
   install_requires=[
       'setuptools',
       'networkx',
       'matplotlib',
       'pandas'
    ],
)
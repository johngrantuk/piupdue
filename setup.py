from setuptools import setup, find_packages
import os

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='piupdue',
    version='0.1.0',
	description='Upload code to Arduino Due from Python.',
    url='https://github.com/johngrantuk/piupdue',
	author='John Grant',
	author_email='johngrantuk@googlemail.com',
    license='MIT',
	packages=find_packages(),
    
    long_description=readme(),
    
)
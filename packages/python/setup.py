"""
Setup for authrelay Python package
"""
from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='authrelay',
    version='1.0.0',
    author='AuthRelay Team',
    description='SDK for AI agents to request human-in-the-loop authentication via AuthRelay',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/authrelay/sdk',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
    ],
    python_requires='>=3.8',
    extras_require={
        'async': ['aiohttp>=3.8.0'],
        'dev': ['pytest>=7.0', 'black', 'mypy', 'pytest-asyncio'],
    },
    project_urls={
        'Bug Reports': 'https://github.com/authrelay/sdk/issues',
        'Documentation': 'https://github.com/authrelay/sdk',
        'Source': 'https://github.com/authrelay/sdk',
    },
)

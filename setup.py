#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="aes-cbc-encryptor",
    version="2.0.0",
    author="Ayan Panda",
    author_email="ayan.panda.inbox@gmail.com",
    description="A high-performance Python file encryption tool implementing AES-128/256 in CBC mode",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ayanpanda-github/AES-CBC_Encrypter",
    py_modules=["encrypt"],
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security :: Cryptography",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=[
        "cryptography>=3.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ]
    },
    entry_points={
        "console_scripts": [
            "aes-encrypt=encrypt:main",
        ],
    },
    keywords="encryption aes cbc file security cryptography streaming memory-optimized",
    project_urls={
        "Bug Reports": "https://github.com/ayanpanda-github/AES-CBC_Encrypter/issues",
        "Source": "https://github.com/ayanpanda-github/AES-CBC_Encrypter",
        "Documentation": "https://github.com/ayanpanda-github/AES-CBC_Encrypter#readme",
    },
)

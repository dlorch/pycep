from setuptools import setup

setup(
    name = "pycep",
    version = "1.0",
    author = "Daniel Lorch",
    author_email = "dlorch@gmail.com",
    description = "Python Inception",
    url = "http://github.com/dlorch/pycep/",
    classifiers = [
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Software Development :: Interpreters"
    ],
    entry_points = {
        'console_scripts': ['pycep=pycep.cli:main'],
    }
)

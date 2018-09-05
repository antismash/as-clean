import os
import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand

short_description = "antiSMASH web service job cleanup script"
long_description = open('README.md').read()

install_requires = [
    'antismash-models >= 0.1.8',
    'redis',
]

tests_require = [
    'pytest',
    'coverage',
    'pytest-cov',
    'mockredispy-kblin >= 2.9.3.3',
]


def read_version():
    for line in open(os.path.join('antismash_clean', '__init__.py'), 'r'):
        if line.startswith('__version__'):
            return line.split('=')[-1].strip().strip("'")


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


setup(
    name='antismash-clean',
    version=read_version(),
    author='Kai Blin',
    author_email='kblin@biosustain.dtu.dk',
    description=short_description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=install_requires,
    tests_require=tests_require,
    cmdclass={'test': PyTest},
    entry_points={
        'console_scripts': [
            'as-clean=antismash_clean.__main__:main',
        ],
    },
    packages=['antismash_clean'],
    url='https://github.com/antismash/as-clean/',
    license='GNU Affero General Public License v3 or later (AGPLv3+)',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: OS Independent',
    ],
    extras_require={
        'testing': tests_require,
    },
)


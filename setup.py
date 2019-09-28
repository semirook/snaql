# coding: utf-8
import os
import pathlib
import sys
from shutil import rmtree
from setuptools import setup, find_packages, Command


DESCRIPTION = 'Transparant *QL usage without ORM'
HERE_PATH = os.path.dirname(os.path.abspath(__file__))
VERSION = '0.4.2'


try:
    with open(os.path.join(HERE_PATH, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(HERE_PATH, 'dist'), ignore_errors=True)
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(VERSION))
        os.system('git push --tags')

        sys.exit()


setup(
    name='snaql',
    version=VERSION,
    author='Roman Zaiev',
    author_email='semirook@gmail.com',
    packages=find_packages(),
    license='MIT',
    url='https://github.com/semirook/snaql',
    description='Transparant *QL usage without ORM',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'Jinja2>=2.9.5',
        'schema>=0.6.5',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    cmdclass={
        'upload': UploadCommand,
    },
)

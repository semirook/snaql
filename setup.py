from setuptools import setup, find_packages


setup(
    name='snaql',
    version='0.1.1',
    author='Roman Semirook',
    author_email='semirook@gmail.com',
    packages=find_packages(),
    license='MIT',
    url='https://github.com/semirook/snaql',
    description='Transparant SQL usage without ORM',
    long_description='Transparant SQL usage without ORM',
    install_requires=[
        'Jinja2==2.8',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

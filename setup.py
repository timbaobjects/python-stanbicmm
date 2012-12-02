from distutils.core import setup

setup(
    name='python-stanbicmm',
    version='0.1',
    packages=['stanbicmm',],
    author="Tim Akinbo",
    author_email="takinbo@timbaobjects.com",
    url='http://pypi.python.org/pypi/python-stanbicmm/',
    license='LICENSE',
    description='A Stanbic Mobile Money interface library',
    long_description=open('README.rst').read(),
    install_requires=[
        "mechanize >= 0.2.5",
    ],
)

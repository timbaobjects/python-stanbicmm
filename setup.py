from distutils.core import setup

setup(
    name='python-stanbicmm',
    version='0.1dev',
    packages=['stanbicmm',],
    url='https://github.com/timbaobjects/python-stanbicmm',
    license='LICENSE',
    description='A Stanbic Mobile Money interface library',
    long_description=open('README.md').read(),
    install_requires=[
        "mechanize == 0.2.5",
    ],
)

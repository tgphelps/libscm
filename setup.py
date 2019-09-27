from setuptools import setup

setup(
    name='libscm',
    version='0.0.1',
    description='Norvig scheme modified for embedding in Python apps',
    packages=['libscm'],
    entry_points={
        'console_scripts': ['scheme = libscm.libscm:main']
    }
)

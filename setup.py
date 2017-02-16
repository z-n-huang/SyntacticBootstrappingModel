from setuptools import setup

setup(name='Main Clause Model',
      version='0.1dev0',
      description="Implements inference algorithms White et al.'s (2017)\
                   Main Clause Model of incremental syntactic bootstrapping",
      url='https://github.com/aaronstevenwhite/MainClauseModel',
      author='Aaron Steven White',
      author_email='aswhite@jhu.edu',
      license='MIT',
      packages=['mainclausemodel'],
      install_requires=['numpy',
                        'scipy',
                        'pandas',
                        'patsy',
                        'theano'],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)

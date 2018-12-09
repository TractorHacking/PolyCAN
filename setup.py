from setuptools import setup

setup(name='polycan',
      version='0.1',
      description='A tool to analyze a CAN log.',
      url='http://github.com/storborg/funniest',
      author='CPCAN',
      author_email='msswanso@calpoly.edu',
      license='Open Source',
      packages=['polycan'],
      zip_safe=False,
      entry_points={
        'console_scripts': [
            'polycan = polycan.polycan:main'
            ]
        },
      )

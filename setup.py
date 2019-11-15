from setuptools import setup

setup(name='polycan',
      version='0.1',
      description='A tool to analyze a CAN log.',
      url='http://github.com/Morgan-Swanson/polycan',
      author='CPCAN',
      author_email='msswanso@calpoly.edu',
      license='Open Source',
      packages=['polycan'],
      install_requires=['tqdm','firebase-admin', 'tabulate',
                        'grpcio', 'numpy', 'scipy', 'pandas',
                        'scikit-learn', 'PyMySQL', 'mysql-connector-python',
                        'matplotlib', 'protobuf', 'python-can', 'pyserial'],
      zip_safe=False,
      entry_points={
        'console_scripts': [
            'polycan = polycan.main:main'
            ]
        },
      )

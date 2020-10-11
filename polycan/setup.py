import setuptools

setuptools.setup(
    name="polycan",
    version="0.2",
    author="Morgan Swanson",
    author_email="msswanso@calpoly.edu",
    description="An ETL based parser for J1939 CAN messages",
    packages=setuptools.find_packages(),
    install_requires=['pandas', 'matplotlib', 'python-can', 'xlrd']
)

    

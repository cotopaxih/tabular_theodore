from setuptools import setup, find_packages

setup(
    name='tabular_theodore',
    version='0.7.9',
    author='Barnabas Paksi',
    author_email='varnavas.shigoto@gmail.com',
    description='Download EU Tender data in a convenient format',
    url='https://github.com/cotopaxih/tabular_theodore',
    packages=find_packages(),
    python_requires='>=3.9', # tested on Python 3.9 only
    install_requires=[
        'pandas>=2.2.2',
        'selenium==4.21.0',
        'CurrencyConverter>=0.17.31',
        'beautifulsoup4>4.0.0',
        'openpyxl>3.1.3',
    ],
)
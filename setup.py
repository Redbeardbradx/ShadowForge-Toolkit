from setuptools import setup, find_packages

setup(
    name='shadowforge',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    description='Utah Viking\'s ethical pentest toolkit',
    author='Redbeard Bradx',
    install_requires=[
        'rich>=13.0',
        'requests>=2.28',
        'scapy>=2.4',
        'stem>=1.8',
    ],
    entry_points={
        'console_scripts': [
            'shadowforge = shadowforge.main:cli_entry',
        ],
    },
)
from setuptools import setup, find_packages

setup(
    name='shadowforge',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    description='Utah Viking\'s ethical hacking toolkit',
    author='Redbeard Brad',
    install_requires=['rich', 'requests', 'scapy'],
)

from setuptools import setup, find_packages

setup(
    name="shadowforge-toolkit",
    version="0.1.0",
    description="Ethical pentest toolkit for isolated lab environments",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "termcolor",
        "requests",
        "shodan",
        "python-nmap",
        "scapy",
        "argparse",
    ],
    entry_points={
        "console_scripts": [
            "shadowforge = shadowforge.main:main",
        ]
    },
)
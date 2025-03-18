from setuptools import setup, find_packages

setup(
    name="azsm",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "azure-identity",
        "azure-mgmt-compute",
        "azure-mgmt-resource",
        "rich"
    ],
    entry_points={
        'console_scripts': [
            'azsm=azsm.__main__:main',
        ],
    },
    author="Bas Berkhout",
    description="Azure Save Money - A tool for analyzing Azure costs and finding savings",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)

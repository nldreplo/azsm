from setuptools import setup, find_packages

setup(
    name="azure_cost_analyzer",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Azure Save Money | azsm package for analyzing Azure resources and calculating potential cost savings.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/azure_cost_analyzer",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        # List your package dependencies here
    ],
)
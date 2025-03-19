from setuptools import setup, find_packages

setup(
    name="indicators-cli",                   
    version="1.0.0",
    author="Syed Ibrahim Omer",
    author_email="syed.ibrahim.omer.2@gmail.com",
    description="CLI tool to calculate stock indicators",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ibitec7/indicators-cli",
    packages=find_packages(),                
    install_requires=[
        "polars",
        "numpy",
        "yfinance",
        "click"                               
    ],
    entry_points={
        'console_scripts': [
            'indicators=src.cli:main',            
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
